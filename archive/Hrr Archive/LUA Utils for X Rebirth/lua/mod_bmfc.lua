package.path = "./?.lua;./lua/?.lua"
local content = [[
# AngelCode Bitmap Font Generator configuration file
fileVersion=1

# font settings
fontName=%s
fontFile=
charSet=0
fontSize=%d
aa=1
scaleH=100
useSmoothing=1
isBold=%d
isItalic=0
useUnicode=1
disableBoxChars=1
outputInvalidCharGlyph=0
dontIncludeKerningPairs=1
useHinting=0
renderFromOutline=0
useClearType=1

# character alignment
paddingDown=0
paddingUp=0
paddingRight=0
paddingLeft=0
spacingHoriz=2
spacingVert=2
useFixedHeight=1
forceZero=0

# output file
outWidth=%d
outHeight=%d
outBitDepth=32
fontDescFormat=0
fourChnlPacked=0
textureFormat=tga
textureCompression=0
alphaChnl=%d
redChnl=%d
greenChnl=%d
blueChnl=%d
invA=0
invR=0
invG=0
invB=0

# outline
outlineThickness=%d

# selected chars
chars=32-126,169,174,1025,1040-1103,1105

# imported icon images
]]

function generate(fontname, size, bold, outline, width, height)
    local a, r, g, b = 2, 4, 4, 4
    if outline > 0 then
        a, r, g, b = 1, 0, 0, 0
    end
    local txt = string.format(content, fontname, size, bold, width, height, a, r, g, b, outline)
    return txt
end
