from __future__ import annotations

import hashlib
import io
import json
import math
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import audio_metrics
import ingest_audio
import make_audio_sheet
from asset_gate import validate_release

REPO = Path(__file__).resolve().parents[1]
RATE = 48000


def pcm16_wav_bytes(samples: list[int], rate: int = RATE) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(rate)
        writer.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buffer.getvalue()


def pcm24_wav_bytes(samples: list[int], *, extra_chunks: bool = True) -> bytes:
    """Handoff-style 24-bit mono WAV: fmt + optional bext/junk + data."""
    data = bytearray()
    for value in samples:
        data += (value & 0xFFFFFF).to_bytes(3, "little")
    fmt = struct.pack("<HHIIHH", 1, 1, RATE, RATE * 3, 3, 24)
    chunks = b"fmt " + struct.pack("<I", len(fmt)) + fmt
    if extra_chunks:
        bext = b"\x00" * 601  # odd size exercises word-alignment padding
        chunks += b"bext" + struct.pack("<I", len(bext)) + bext + b"\x00"
        chunks += b"junk" + struct.pack("<I", 28) + b"\x00" * 28
    chunks += b"data" + struct.pack("<I", len(data)) + bytes(data)
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks


def sine24(freq: float, amplitude: float, seconds: float) -> list[int]:
    frames = int(round(seconds * RATE))
    scale = 8388608.0
    return [
        max(-8388608, min(8388607, round(amplitude * scale * math.sin(2 * math.pi * freq * n / RATE))))
        for n in range(frames)
    ]


class WavReaderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.wav"

    def test_reads_pcm24_with_extra_chunks_and_padding(self) -> None:
        samples = [0, 1, -1, 8388607, -8388608]
        self.path.write_bytes(pcm24_wav_bytes(samples))
        info = audio_metrics.read_wav(self.path)
        self.assertEqual((RATE, 1, 24, 5), (info.sample_rate_hz, info.channels, info.bit_depth, info.frames))
        self.assertEqual(tuple(samples), info.samples)

    def test_reads_pcm16(self) -> None:
        self.path.write_bytes(pcm16_wav_bytes([0, 32767, -32768]))
        info = audio_metrics.read_wav(self.path)
        self.assertEqual((16, (0, 32767, -32768)), (info.bit_depth, info.samples))

    def test_rejects_malformed_files(self) -> None:
        cases = {
            "not riff": b"JUNK" + b"\x00" * 20,
            "riff size lie": b"RIFF" + struct.pack("<I", 99) + b"WAVE",
        }
        for label, data in cases.items():
            with self.subTest(label):
                self.path.write_bytes(data)
                with self.assertRaises(audio_metrics.WavError):
                    audio_metrics.read_wav(self.path)

    def test_rejects_unsupported_formats(self) -> None:
        good = bytearray(pcm16_wav_bytes([0] * 4))
        float_fmt = bytearray(good)
        float_fmt[20:22] = struct.pack("<H", 3)  # IEEE float tag
        stereo = bytearray(good)
        stereo[22:24] = struct.pack("<H", 2)
        for label, data in (("format tag", float_fmt), ("channels", stereo)):
            with self.subTest(label):
                self.path.write_bytes(bytes(data))
                with self.assertRaises(audio_metrics.WavError):
                    audio_metrics.read_wav(self.path)

    def test_rejects_missing_or_duplicate_chunks(self) -> None:
        base = pcm16_wav_bytes([0] * 4)
        no_data = base[: base.index(b"data")]
        no_data = no_data[:4] + struct.pack("<I", len(no_data) - 8) + no_data[8:]
        self.path.write_bytes(no_data)
        with self.assertRaises(audio_metrics.WavError):
            audio_metrics.read_wav(self.path)

    def test_rejects_partial_frame(self) -> None:
        raw = bytearray(pcm24_wav_bytes([0, 0], extra_chunks=False))
        # extend the data chunk size by one byte and append one byte
        offset = raw.index(b"data") + 4
        size = struct.unpack_from("<I", raw, offset)[0]
        struct.pack_into("<I", raw, offset, size + 1)
        raw += b"\x00"
        struct.pack_into("<I", raw, 4, len(raw) - 8)
        self.path.write_bytes(bytes(raw))
        with self.assertRaises(audio_metrics.WavError):
            audio_metrics.read_wav(self.path)


class ConversionLawTest(unittest.TestCase):
    def test_known_values(self) -> None:
        cases = {
            0: 0,
            256: 1,  # 256*32767/2^23 = 0.99997 -> 1
            -256: -1,
            8388607: 32767,  # max positive
            -8388608: -32767,  # scale is peak-preserving, not overflowing
            4194304: 16384,  # the only positive tie (16383.5 -> half-even 16384)
            -4194304: -16384,
        }
        wav = ingest_audio.convert_pcm24_to_pcm16(tuple(cases))
        with wave.open(io.BytesIO(wav), "rb") as reader:
            raw = reader.readframes(reader.getnframes())
        converted = struct.unpack(f"<{len(raw) // 2}h", raw)
        self.assertEqual(tuple(cases.values()), converted)

    def test_header_is_canonical_44_bytes(self) -> None:
        wav = ingest_audio.convert_pcm24_to_pcm16((0, 0))
        self.assertEqual(44 + 4, len(wav))
        self.assertEqual(b"RIFF", wav[:4])
        self.assertEqual(b"WAVEfmt ", wav[8:16])
        self.assertEqual(b"data", wav[36:40])

    def test_conversion_is_deterministic(self) -> None:
        samples = tuple(sine24(313.0, 0.7, 0.01))
        self.assertEqual(
            ingest_audio.convert_pcm24_to_pcm16(samples),
            ingest_audio.convert_pcm24_to_pcm16(samples),
        )


class MeterValidationTest(unittest.TestCase):
    """The pre-registered vectors V1-V6 (rationale section 4)."""

    def test_all_vectors_pass(self) -> None:
        self.assertEqual([], audio_metrics.meter_validation_failures())

    def test_vector_v1_analytic_expectation(self) -> None:
        # independent re-statement of the derivation: -9.0309 LUFS at a=0.5
        self.assertAlmostEqual(
            -9.0309, audio_metrics._analytic_sine_lufs(0.5, 997.0), places=3
        )

    def test_meter_catches_broken_gating(self) -> None:
        # sanity that V3 would catch a meter without the absolute gate:
        # an ungated mean over sine+silence reads ~3 LU lower than gated.
        sine = audio_metrics._sine_pcm16(997.0, 0.1, 3.0)
        padded = audio_metrics.WavInfo(
            RATE, 1, 16, sine.frames * 2, sine.samples + (0,) * sine.frames
        )
        gated = audio_metrics.integrated_lufs(padded)
        normalized = [s / 32768.0 for s in padded.samples]
        weighted = audio_metrics._biquad(
            audio_metrics._biquad(normalized, audio_metrics.STAGE1_B, audio_metrics.STAGE1_A),
            audio_metrics.STAGE2_B,
            audio_metrics.STAGE2_A,
        )
        blocks = audio_metrics._block_mean_squares(weighted)
        ungated = audio_metrics._loudness(sum(blocks) / len(blocks))
        self.assertGreater(gated - ungated, 2.0)

    def test_short_file_has_no_integrated_loudness(self) -> None:
        short = audio_metrics._sine_pcm16(997.0, 0.5, 0.2)
        self.assertIsNone(audio_metrics.integrated_lufs(short))

    def test_meter_rejects_wrong_rate(self) -> None:
        info = audio_metrics.WavInfo(44100, 1, 16, 44100, (0,) * 44100)
        with self.assertRaises(audio_metrics.WavError):
            audio_metrics.integrated_lufs(info)

    def test_sample_peak(self) -> None:
        info = audio_metrics.WavInfo(RATE, 1, 16, 3, (0, -16384, 100))
        self.assertAlmostEqual(-6.0206, audio_metrics.sample_peak_dbfs(info), places=4)
        silent = audio_metrics.WavInfo(RATE, 1, 16, 2, (0, 0))
        self.assertEqual(-math.inf, audio_metrics.sample_peak_dbfs(silent))


class SyntheticLaneTest(unittest.TestCase):
    """Full ingest -> gate -> metrics -> sheet over a synthetic handoff."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.handoff = Path(self.temp.name) / "handoff"
        self.handoff.mkdir(parents=True)
        (self.root / "tools").mkdir(parents=True)
        (self.root / "manifests").mkdir()
        # the release builder pins THIS repo's real exporter bytes
        exporter = (REPO / "tools" / "ingest_audio.py").read_bytes()
        (self.root / "tools" / "ingest_audio.py").write_bytes(exporter)
        baseline = {"game_commit": "b" * 40}
        (self.root / "manifests" / "runtime-baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )

        assets = []
        self.originals: dict[str, bytes] = {}
        specs = (
            ("mstem_calm_6s", sine24(220.0, 0.2, 2.0) * 3, 6.0, "calm loop", "music bed"),
            ("msfx_stinger_2s", sine24(660.0, 0.35, 2.0), 2.0, "stinger", "sfx"),
            ("mui_confirm_200ms", sine24(880.0, 0.1, 0.2), 0.2, "confirm", "ui"),
        )
        for asset_id, samples, dur_s, role, band in specs:
            original = pcm24_wav_bytes(samples)
            self.originals[asset_id] = original
            (self.handoff / f"{asset_id}.wav").write_bytes(original)
            twin = ingest_audio.convert_pcm24_to_pcm16(tuple(samples))
            source_info = audio_metrics.read_wav(self.handoff / f"{asset_id}.wav")
            assets.append(
                {
                    "id": asset_id,
                    "role": role,
                    "level_band": band,
                    "file": f"{asset_id}.wav",
                    "format": "WAV PCM 24-bit mono 48000 Hz",
                    "dur_s": dur_s,
                    "frames": source_info.frames,
                    "sha256": hashlib.sha256(original).hexdigest(),
                    "peak_dbfs": round(audio_metrics.sample_peak_dbfs(source_info), 2),
                    "rms_dbfs": -20.0,
                    "evaluation_twin": {
                        "path": f"stems/{asset_id}.wav",
                        "sha256": hashlib.sha256(twin).hexdigest(),
                        "pinned_commit": "abc1234",
                    },
                    "source_revision": f"test-{asset_id}",
                }
            )
        manifest_bytes = json.dumps({"assets": assets}, indent=2).encode("utf-8")
        (self.handoff / "manifest.json").write_bytes(manifest_bytes)
        self.manifest_md5 = hashlib.md5(manifest_bytes).hexdigest()
        # the tool pins the REAL handoff md5; patch the pin for the synthetic lane
        self._original_md5 = ingest_audio.HANDOFF_MANIFEST_MD5
        ingest_audio.HANDOFF_MANIFEST_MD5 = self.manifest_md5
        self.addCleanup(setattr, ingest_audio, "HANDOFF_MANIFEST_MD5", self._original_md5)

    def _run_all(self) -> Path:
        status = ingest_audio.main(
            [
                "--root", str(self.root),
                "--handoff", str(self.handoff),
                "--stage", "all",
                "--commit", "a" * 40,
            ]
        )
        self.assertEqual(0, status)
        return self.root / "exports" / "audio-v1" / "release.json"

    def test_ingest_builds_gate_valid_release(self) -> None:
        release_path = self._run_all()
        release = json.loads(release_path.read_text(encoding="utf-8"))
        self.assertEqual([], validate_release(release_path, self.root))
        for entry in release["exports"]:
            self.assertEqual(entry["sha256"], entry["conversion"]["evaluation_twin_sha256"])
        stem = release["exports"][0]
        self.assertEqual("audio", stem["kind"])
        self.assertEqual(0, stem["frames"] % audio_metrics.BAR_FRAMES)
        confirm = release["exports"][2]
        self.assertIsNone(confirm["loudness"]["lufs_integrated"])

    def test_ingest_is_deterministic_across_runs(self) -> None:
        release_path = self._run_all()
        first = {
            path.name: path.read_bytes()
            for path in sorted((self.root / "exports" / "audio-v1").iterdir())
        }
        self._run_all()
        second = {
            path.name: path.read_bytes()
            for path in sorted((self.root / "exports" / "audio-v1").iterdir())
        }
        self.assertEqual(first, second)
        self.assertIn("release.json", first)

    def test_ingest_stops_on_md5_mismatch(self) -> None:
        ingest_audio.HANDOFF_MANIFEST_MD5 = "0" * 32
        status = ingest_audio.main(
            ["--root", str(self.root), "--handoff", str(self.handoff), "--stage", "sources"]
        )
        self.assertEqual(1, status)
        self.assertFalse((self.root / "sources" / "audio-v1").exists())

    def test_ingest_stops_on_original_hash_mismatch(self) -> None:
        target = self.handoff / "msfx_stinger_2s.wav"
        raw = bytearray(target.read_bytes())
        raw[-1] ^= 0x01
        target.write_bytes(bytes(raw))
        status = ingest_audio.main(
            ["--root", str(self.root), "--handoff", str(self.handoff), "--stage", "sources"]
        )
        self.assertEqual(1, status)

    def test_ingest_stops_when_twin_hash_cannot_be_reproduced(self) -> None:
        manifest = json.loads((self.handoff / "manifest.json").read_text(encoding="utf-8"))
        manifest["assets"][0]["evaluation_twin"]["sha256"] = "0" * 64
        raw = json.dumps(manifest, indent=2).encode("utf-8")
        (self.handoff / "manifest.json").write_bytes(raw)
        ingest_audio.HANDOFF_MANIFEST_MD5 = hashlib.md5(raw).hexdigest()
        status = ingest_audio.main(
            [
                "--root", str(self.root),
                "--handoff", str(self.handoff),
                "--stage", "all",
                "--commit", "a" * 40,
            ]
        )
        self.assertEqual(1, status)
        self.assertFalse((self.root / "exports" / "audio-v1" / "release.json").exists())

    def test_gate_catches_corrupted_export(self) -> None:
        release_path = self._run_all()
        target = self.root / "exports" / "audio-v1" / "msfx_stinger_2s.wav"
        raw = bytearray(target.read_bytes())
        raw[-1] ^= 0x01
        target.write_bytes(bytes(raw))
        errors = "\n".join(validate_release(release_path, self.root))
        self.assertIn("sha256 does not match the export", errors)

    def test_gate_catches_audio_law_violations(self) -> None:
        release_path = self._run_all()
        release = json.loads(release_path.read_text(encoding="utf-8"))
        entry = release["exports"][0]
        entry["format"]["bit_depth"] = 24
        entry["frames"] = entry["frames"] + 1
        entry["conversion"]["evaluation_twin_sha256"] = "f" * 64
        entry["conversion"]["reproduces_evaluation_twin"] = False
        entry["loudness"]["sample_peak_dbfs"] = 3.0
        entry["role"] = ""
        del entry["provenance"]["upstream"]
        release_path.write_text(json.dumps(release), encoding="utf-8")
        errors = "\n".join(validate_release(release_path, self.root))
        for expected in (
            "format must be exactly",
            "dur_s must equal frames/48000",
            "music stem must be bar-exact",
            "export sha256 must equal the evaluation-twin sha256",
            "reproduces_evaluation_twin must be true",
            "sample_peak_dbfs must be a number <= 0",
            "role must be a non-empty string",
            "provenance.upstream must be an object",
            "WAV has",
        ):
            self.assertIn(expected, errors)

    def test_gate_catches_missing_source_and_bad_upstream(self) -> None:
        release_path = self._run_all()
        release = json.loads(release_path.read_text(encoding="utf-8"))
        entry = release["exports"][1]
        entry["source"]["sha256"] = "0" * 64
        entry["provenance"]["upstream"]["handoff_commit"] = "short"
        entry["provenance"]["upstream"]["handoff_manifest_md5"] = "nope"
        release_path.write_text(json.dumps(release), encoding="utf-8")
        errors = "\n".join(validate_release(release_path, self.root))
        for expected in (
            "source.sha256 does not match the source file",
            "handoff_commit must be a full lowercase",
            "handoff_manifest_md5 must be lowercase MD5",
        ):
            self.assertIn(expected, errors)

    def test_metrics_check_and_sheet_are_deterministic(self) -> None:
        self._run_all()
        reviews = self.root / "reviews" / "audio-v1"
        args = [
            "--root", str(self.root),
            "--handoff-manifest", "sources/audio-v1/handoff-manifest.json",
            "--check",
        ]
        self.assertEqual(0, audio_metrics.main(args))
        first = (reviews / "audio-metrics.json").read_bytes()
        document = json.loads(first.decode("utf-8"))
        self.assertEqual([], document["integrity_failures"])
        self.assertEqual([], document["measurement_failures"])
        confirm = [f for f in document["files"] if f["asset_id"] == "mui_confirm_200ms"][0]
        self.assertIsNone(confirm["lufs_integrated"])
        self.assertIn("400 ms", confirm["lufs_note"])
        self.assertEqual(0, audio_metrics.main(args))
        self.assertEqual(first, (reviews / "audio-metrics.json").read_bytes())

        sheet_args = ["--root", str(self.root)]
        self.assertEqual(0, make_audio_sheet.main(sheet_args))
        sheet_first = (reviews / "audio-sheet.png").read_bytes()
        self.assertEqual(0, make_audio_sheet.main(sheet_args))
        self.assertEqual(sheet_first, (reviews / "audio-sheet.png").read_bytes())

    def test_metrics_check_flags_twin_and_peak_disagreement(self) -> None:
        self._run_all()
        manifest_path = self.root / "sources" / "audio-v1" / "handoff-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["assets"][1]["evaluation_twin"]["sha256"] = "0" * 64
        manifest["assets"][2]["peak_dbfs"] = -1.0
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        status = audio_metrics.main(
            [
                "--root", str(self.root),
                "--handoff-manifest", "sources/audio-v1/handoff-manifest.json",
                "--check",
            ]
        )
        self.assertEqual(1, status)
        document = json.loads(
            (self.root / "reviews" / "audio-v1" / "audio-metrics.json").read_text(
                encoding="utf-8"
            )
        )
        failures = "\n".join(document["integrity_failures"])
        self.assertIn("do not reproduce the evaluation twin", failures)
        self.assertIn("sample peak", failures)


class RealArtifactRegressionTest(unittest.TestCase):
    """Committed audio-v1 artifacts regenerate byte-identical (skip-guarded)."""

    HANDOFF = REPO.parent / "game-two-audio" / "handoff" / "audio-v1"

    def setUp(self) -> None:
        if not (REPO / "exports" / "audio-v1" / "release.json").is_file():
            self.skipTest("audio-v1 release is not banked yet")

    def test_release_manifest_matches_gate(self) -> None:
        self.assertEqual(
            [], validate_release(REPO / "exports" / "audio-v1" / "release.json", REPO)
        )

    def test_sources_match_handoff_package(self) -> None:
        if not self.HANDOFF.is_dir():
            self.skipTest("sibling game-two-audio handoff is unavailable")
        manifest_raw = (REPO / "sources" / "audio-v1" / "handoff-manifest.json").read_bytes()
        self.assertEqual(
            ingest_audio.HANDOFF_MANIFEST_MD5, hashlib.md5(manifest_raw).hexdigest()
        )
        self.assertEqual(manifest_raw, (self.HANDOFF / "manifest.json").read_bytes())
        for asset in json.loads(manifest_raw.decode("utf-8"))["assets"]:
            staged = (REPO / "sources" / "audio-v1" / asset["file"]).read_bytes()
            self.assertEqual(
                asset["sha256"], hashlib.sha256(staged).hexdigest(), asset["id"]
            )

    def test_conversion_regenerates_committed_exports(self) -> None:
        manifest = json.loads(
            (REPO / "sources" / "audio-v1" / "handoff-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        for asset in manifest["assets"]:
            source = audio_metrics.read_wav(REPO / "sources" / "audio-v1" / asset["file"])
            rebuilt = ingest_audio.convert_pcm24_to_pcm16(source.samples)
            committed = (REPO / "exports" / "audio-v1" / f"{asset['id']}.wav").read_bytes()
            self.assertEqual(committed, rebuilt, asset["id"])
            self.assertEqual(
                asset["evaluation_twin"]["sha256"],
                hashlib.sha256(rebuilt).hexdigest(),
                asset["id"],
            )

    def test_metrics_and_sheet_regenerate_byte_identical(self) -> None:
        metrics_path = REPO / "reviews" / "audio-v1" / "audio-metrics.json"
        sheet_path = REPO / "reviews" / "audio-v1" / "audio-sheet.png"
        if not metrics_path.is_file() or not sheet_path.is_file():
            self.skipTest("audio-v1 review artifacts are not banked yet")
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "audio-metrics.json"
            status = audio_metrics.main(["--root", str(REPO), "--out", str(out)])
            self.assertEqual(0, status)
            self.assertEqual(metrics_path.read_bytes(), out.read_bytes())
            sheet_out = Path(temp) / "audio-sheet.png"
            status = make_audio_sheet.main(["--root", str(REPO), "--out", str(sheet_out)])
            self.assertEqual(0, status)
            self.assertEqual(sheet_path.read_bytes(), sheet_out.read_bytes())

    def test_exporter_pin_matches_working_tree(self) -> None:
        release = json.loads(
            (REPO / "exports" / "audio-v1" / "release.json").read_text(encoding="utf-8")
        )
        pinned = release["toolchain"]["exporter_sha256"]
        actual = hashlib.sha256((REPO / "tools" / "ingest_audio.py").read_bytes()).hexdigest()
        self.assertEqual(pinned, actual, "ingest_audio.py drifted after banking")


if __name__ == "__main__":
    unittest.main()
