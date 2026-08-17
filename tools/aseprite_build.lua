-- Build a native .aseprite source from a generated Lua pixel-data chunk.
-- Headless use only:
--   aseprite -b --script-param data=<pixels.lua> --script-param out=<file.aseprite> \
--            --script tools/aseprite_build.lua
local data_path = app.params["data"]
local out_path = app.params["out"]
assert(data_path and #data_path > 0, "missing --script-param data=<pixels.lua>")
assert(out_path and #out_path > 0, "missing --script-param out=<file.aseprite>")

local chunk = assert(loadfile(data_path))
local spec = chunk()
assert(type(spec) == "table", "data chunk must return a table")
assert(spec.width == 32 and spec.height == 32, "creature canvas must be 32x32")

local sprite = Sprite(spec.width, spec.height, ColorMode.RGB)
local image = sprite.cels[1].image
for _, p in ipairs(spec.pixels) do
  image:drawPixel(p[1], p[2], app.pixelColor.rgba(p[3], p[4], p[5], 255))
end
sprite:saveAs(out_path)
