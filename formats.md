# File Formats

Reverse-engineered by "arc_"

## Data Types

- `vec3d`: float x, float y, float z
- `vec4d`: float x, float y, float z, float w
- `quat`: float x, float y, float z, float w
- `quat16`: int16 x, int16 y, int16 z, int16 w; fX = x / 32767
- `string`: uint32 len, char[len]
- `matrix44`: `vec4d` col1, `vec4d` col2, `vec4d` col3, `vec4d` pos

## XMF

### XMF Summary

Xu Mesh Files (*.xmf) contain non-NPC meshes. They can be somewhat animated through `*.ani` files, including moving/rotating/scaling the entire mesh over time, but do not contain bones or morph targets.

Examples include:

- ships
- station parts
- asteroids

They are quite close to DirectX. Once decompressed, their content can be directly copied to a DirectX vertex or index buffer.

### XMF Overview

Each file consists of a header, a number of buffer descriptions, and an equal number of buffer contents.

A buffer can be a vertex buffer (vertex positions/normals/texture coordinates/...) or an index buffer (indices into the vertex buffer which determine the polygons).

There can be one vertex buffer that stores all attributes of all vertices, or multiple vertex buffers where each buffer stores one particular attribute for all vertices.

Collision meshes (*-collision.xmf) must have exactly one vertex attribute, namely D3DDECLUSAGE_POSITION (0) stored as D3DDECLTYPE_FLOAT3 (2).
This attribute must be stored in the type/usageIndex/format fields of the DataBufferDesc structure, not in the VertexDeclElement array. **Not following this rule causes the game to crash!**

### XMF Specification

#### XMF Header

```text
byte magic[4]             = "XUMF"  // Xu Mesh File
byte version              = 3
byte bBigEndian           = 0
byte dataBufferDescOffset = 0x40    // file offset of first data buffer desc
byte pad
byte numDataBuffers                 // typically 2, but may be more. there is always one index buffer and one or more vertex buffers.
                                    // if there are multiple vertex buffers, these merely define additional attributes for the same
                                    // vertices, not more vertices.

byte dataBufferDescSize             // size of one data buffer description. has a maximum value of 0xBC (= sizeof(DataBufferDesc)), but some files use less,
                                    // in which case the remaining DataBufferDesc fields should be set to 0.
byte numMaterials
byte materialSize         = 0x88    // size of one material assignment
byte pad[10]
int32 primitiveType       = 4       // D3DPRIMITIVETYPE; determines how the index buffer is used to draw polygons. 4 = triangle list

byte pad[dataBufferDescOffset-0x1A]
```

#### XMF DataBufferDesc

```text
DataBufferDesc[numDataBuffers]      // describes a DirectX 9 vertex or index buffer

    int32 type                      // 0x1E -> index buffer, otherwise vertex buffer
                                    // For vertex buffers with numVertexElements = 0, indicates the usage of a single implicit element. The type
                                    // should be mapped to a D3DDECLUSAGE as follows:
                                    //   type    D3DDECLUSAGE
                                    //   ------------------------
                                    //   0, 1    POSITION
                                    //   2, 3    NORMAL
                                    //   4       TANGENT
                                    //   5       BINORMAL
                                    //   8       COLOR
                                    //   20      PSIZE
                                    //   others  TEXCOORD

    int32 usageIndex                // for vertex buffers with numVertexElements = 0, indicates the usage index of the single implicit element
    int32 dataOffset                // file offset = dataBufferDescOffset + numDataBuffers*dataBufferDescSize + numMaterials*materialSize + dataOffset
    int32 bCompressed               // if 1, the data is compressed using zlib's compress() function and can be uncompressed with uncompress()
    byte pad[4]
    int32 format                    // for index buffers, this is the index format: 0x1E -> 16-bit indices, 0x1F -> 32-bit indices.
                                    // for vertex buffers with numVertexElements = 0, this is the type (D3DDECLTYPE) of the single implicit element.
                                    // otherwise 0x20.

    int32 compressedDataSize        // size of the buffer data in the file. equal to uncompressed size if bCompressed = 0
    int32 itemsPerSection           // number of vertices/indices
    int32 itemSize                  // size in bytes of a single vertex/index
    int32 numSections = 1
    byte pad[16]
    int32 numVertexElements         // for the vertex buffer, number of elements in the DirectX vertex declaration. May be 0,
                                    // in which case a single declaration is built using type, usageIndex and format.

    VertexDeclElement[16]           // fixed size array, only the first numVertexElements items are used. each item is mapped to a D3DVERTEXELEMENT9
        int32 type                  // D3DDECLTYPE
        byte usage                  // D3DDECLUSAGE
        byte usageIndex
        byte pad[2]
```

#### XMF Materials

```text
Material[numMaterials]
    int32 firstIndex                // index of the first index in the index buffer which the material applies to (multiple of 3)
    int32 numIndices                // number of indices, starting at firstIndex, which the material applies to (multiple of 3)
                                    // the sum of the numIndices of all Materials should be equal to the itemsPerSection of the index buffer

    char name[128]                  // materialCollection + "." + materialName as found in material_library.xml
```

for each data buffer:
    byte bufferData[compressedDataSize]     // content of the DirectX vertex/index buffer, zlib-compressed if bCompressed = 1.
                                            // the uncompressed size is numSections * itemsPerSection * itemSize.

## XAC

```text
file:
    byte magic[4] = 58 41 43 20 ("XAC ")
    byte majorVersion = 1
    byte minorVersion = 0
    byte bBigEndian
    byte multiplyOrder

    chunk[...]
        int32 chunkType
        int32 length (sometimes incorrect!)
        int32 version
        byte data[length]

chunk 7: metadata (v2)
    uint32 repositionMask
        1 = repositionPos
        2 = repositionRot
        4 = repositionScale
    int32 repositioningNode
    byte exporterMajorVersion
    byte exporterMinorVersion
    byte unused[2]
    float retargetRootOffset
    string sourceApp
    string origFileName
    string exportDate
    string actorName

chunk B: node hierarchy (v1)
    int32 numNodes
    int32 numRootNodes (number of nodes with parentId = -1)

    NodeData[numNodes]
        quat rotation
        quat scaleRotation
        vec3d position
        vec3d scale
        float unused[3]
        int32 -1 (?)
        int32 -1 (?)
        int32 parentNodeId (index of parent node or -1 for root nodes)
        int32 numChildNodes (number of nodes with parentId = this node's index)
        int32 bIncludeInBoundsCalc
        matrix44 transform
        float fImportanceFactor
        string name

chunk D: material totals (v1)
    int32 numTotalMaterials
    int32 numStandardMaterials
    int32 numFxMaterials

chunk 3: material definition (v2)
    vec4d ambientColor
    vec4d diffuseColor
    vec4d specularColor
    vec4d emissiveColor
    float shine
    float shineStrength
    float opacity
    float ior
    byte bDoubleSided
    byte bWireframe
    byte unused
    byte numLayers
    string name

    Layer[numLayers]:
        float amount
        float uOffset
        float vOffset
        float uTiling
        float vTiling
        float rotationInRadians
        int16 materialId (index of the material this layer belongs to = number of preceding chunk 3's)
        byte mapType
        byte unused
        string texture

chunk 1: mesh (v1)
    int32 nodeId
    int32 numInfluenceRanges
    int32 numVertices (total number of vertices of submeshes)
    int32 numIndices  (total number of indices of submeshes)
    int32 numSubMeshes
    int32 numAttribLayers
    byte bIsCollisionMesh (each node can have 1 visual mesh and 1 collision mesh)
    byte pad[3]

    VerticesAttribute[numAttribLayers]
        int32 type (determines meaning of data)
            0 = positions (vec3d)
            1 = normals (vec3d)
            2 = tangents (vec4d)
            3 = uv coords (vec2d)
            4 = 32-bit colors (uint32)
            5 = influence range indices (uint32) - index into the InfluenceRange[] array of chunk 2, indicating the bones that affect it
            6 = 128-bit colors

            typically: 1x positions, 1x normals, 2x tangents, 2x uv, 1x colors, 1x influence range indices
        int32 attribSize (size of 1 attribute, for 1 vertex)
        byte bKeepOriginals
        byte bIsScaleFactor
        byte pad[2]
        byte data[numVertices * attribSize]

    SubMesh[numSubMeshes]
        int32 numIndices
        int32 numVertices
        int32 materialId
        int32 numBones
        int32 relativeIndices[numIndices] (actual index = relative index + total number of vertices of preceding submeshes. each group of 3 sequential indices (vertices) defines a polygon)
        int32 boneIds[numBones] (unused)

chunk 2: skinning (v3)
    int32 nodeId
    int32 numLocalBones (number of distinct boneId's in InfluenceData)
    int32 numInfluences
    byte bIsForCollisionMesh
    byte pad[3]

    InfluenceData[numInfluences]
        float fWeight (0..1)   (for every vertex, the resulting transformed position is calculated for every influencing bone;
        int16 boneId            the final position is the weighted average of these positions using fWeight as weight)
        byte pad[2]

    InfluenceRange[bIsForCollisionMesh ? nodes[nodeId].colMesh.numInfluenceRanges : nodes[nodeId].visualMesh.numInfluenceRanges]
        int32 firstInfluenceIndex (index into InfluenceData)
        int32 numInfluences (number of InfluenceData entries relevant for one or more vertices, starting at firstInfluenceIndex)

chunk C: morph targets (v1)
    int32 numMorphTargets
    int32 lodMorphTargetIdx (presumably always 0; this is the index of a *collection* of numMorphTargets morph targets, not an
                             individual target, and an EmoActor only has one such collection)

    MorphTarget[numMorphTargets]
        float fRangeMin (at runtime, fMorphAmount must be >= fRangeMin)
        float fRangeMax (at runtime, fMorphAmount must be <= fRangeMax)
        int32 lodLevel (LOD of visual mesh; presumably always 0)
        int32 numDeformations
        int32 numTransformations
        int32 phonemeSetBitmask (indicates which phonemes the morph target can be used for - facial animation)
            0x1: neutral
            0x2: M, B, P, X
            0x4: AA, AO, OW
            0x8: IH, AE, AH, EY, AY, H
            0x10: AW
            0x20: N, NG, CH, J, DH, D, G, T, K, Z, ZH, TH, S, SH
            0x40: IY, EH, Y
            0x80: UW, UH, OY
            0x100: F, V
            0x200: L, EL
            0x400: W
            0x800: R, ER

        string name

        Deformation[numDeformations]
            int32 nodeId
            float fMinValue
            float fMaxValue
            int32 numVertices
            DeformVertex16 positionOffsets[numVertices]
                uint16 x (fXOffset = fMinValue + (fMaxValue - fMinValue)*(x / 65535); vecDeformedPos.fX = vecPos.fX + fXOffset*fMorphAmount)
                uint16 y
                uint16 z
            DeformVertex8 normalOffsets[numVertices]
                byte x (fXOffset = x/127.5 - 1.0; vecDeformedNormal.fX = vecNormal.fX + fXOffset * fMorphAmount)
                byte y
                byte z
            DeformVertex8 tangentOffsets[numVertices] (offsets for first tangent)
            uint32 vertexIndices[numVertices] (index of the node's visual mesh vertex which the offsets apply to)

        Transformation[numTransformations] (appears to be unused, i.e. numTransformations = 0)
            int32 nodeId
            quat rotation
            quat scaleRotation
            vec3d pos
            vec3d scale
```

## XPM

```text
file:
    byte magic[4] = 58 50 4D 20 ("XPM ")
    byte majorVersion = 1
    byte minorVersion = 0
    byte bBigEndian
    byte pad

    chunk[...]
        int32 chunkType
        int32 length
        int32 version
        byte data[length]

chunk 65: metadata (v1)
    int32 fps
    byte exporterMajorVersion
    byte exporterMinorVersion
    byte pad[2]
    string sourceApp
    string origFilePath
    string exportDate
    string motionName

chunk 66: deformation animation (v1)
    int32 numMorphTargetAnims
    MorphTargetAnim[numMorphTargetAnims]:
        float fPoseWeight
        float fMinWeight
        float fMaxWeight
        int32 phonemeSetBitmask (see .xac)
        int32 numKeys
        string morphTargetName

        Key[numKeys]:
            float fTime
            uint16 amount (/ 65535)
            byte pad[2]
```

## XSM

```text
file:
    byte magic[4] = 58 53 4D 20 ("XSM ")
    byte majorVersion = 1
    byte minorVersion = 0
    byte bBigEndian
    byte pad

    chunk[...]
        int32 chunkType
        int32 length
        int32 version
        byte data[length]

chunk C9: metadata (v2)
    float unused = 1.0f
    float fMaxAcceptableError
    int32 fps
    byte exporterMajorVersion
    byte exporterMinorVersion
    byte pad[2]
    string sourceApp
    string origFileName
    string exportDate
    string motionName

chunk CA: bone animation (v2)
    int32 numSubMotions
    SkeletalSubMotion[numSubMotions]:
        quat16 poseRot
        quat16 bindPoseRot
        quat16 poseScaleRot
        quat16 bindPoseScaleRot
        vec3D posePos
        vec3D poseScale
        vec3D bindPosePos
        vec3D bindPoseScale
        int32 numPosKeys
        int32 numRotKeys
        int32 numScaleKeys
        int32 numScaleRotKeys
        float fMaxError
        string nodeName

        // fTime of first item in each array must be 0

        PosKey[numPosKeys]:
            vec3d pos
            float fTime

        RotKey[numRotKeys]:
            quat16 rot
            float fTime

        ScaleKey[numScaleKeys]:
            vec3d scale
            float fTime

        ScaleRotKey[numScaleRotKeys]:
            quat16 rot
            float fTime
```

## Anark (Rebirth?)

```text
Hashing algorithm:

int Hash(const char* psz)
{
    int result = 0;
    for (int i = 0; i < 100; i++)
    {
        char c = psz[i];
        result = result*0x1003F + c;
        if (!c)
            break;
    }
    return result;
}

string:
    int size
    char data[size]   (zero-terminated in .bgp, not in .bgf)

.bgp (Binary Game Plan):
    byte endianness = 0
    int numAssets
    Asset[numAssets]
        string type
        string id
        string bgfFilePath

    int numStates
    State[numStates]
        string id
        int numPreludeActions
        Action[numPreludeActions]
            string action = preload|show|hide|kill|pause|resume|lockupdate|unlockupdate
            string assetId
        int numTransitions
        Transition[numTransitions]
            string toStateId
            string event
            int numActions
            Action[numActions]
        int numPostludeActions
        Action[numPostludeActions]

BGF Lua registry:
    1: AnarkBgf* pBgf
    2: table containing elements: { [i] = { element = userdata(pElement), __scriptIndex = i } }
    3: AnarkLuaLogger* pLogger
    4: &AnarkLuaEngine.eventCallbacksList
    5: &AnarkLuaEngine.changeCallbacksList
    6: event callback table: { [i] = func }

.bgf (Binary Game Face):
    header
        byte endianness = 0
        byte ignored = 4
        int headerSize = 0x1A
        byte magic[8] = "AnarkBGF"
        int version = 3
        int ignored = 0
        short width
        short height
        byte fitMode (0: no scaling?, 1: fit to width, 2: fit to width and height)
        int numSceneItems
        byte ignored = 0

    memory section
        int sectionSize = 0x64
        int counts[0x13]
            elements:
                0: number of small elements
                1: number of large elements
                2: number of attributes
            contracts:
                3: number of contracts
                4: number of event names
            strings:
                6: number of strings
            animations:
                8: number of animations
                9: number of animation keyframes
            logic:
                10: number of logics
                11: ?
                12: ?
            params:
                13: number of params
            slides:
                14: number of slides
                15: number of slide element refs
                16: number of slide element attributes
                17: number of slide element animation refs
                18: number of paddings: number of elements with an uneven number of animations, not counting the last element
        int ignored[6]

    strings section
        int sectionSize
        string str[memory.counts[6]]

    elements section
        int sectionSize
        Element[memory.counts[0] + memory.counts[1]]
            int nameHash     (see "name" attributes in the .dae)
            int parentIdx    (-1 for root elements)
            int sceneItemId  (0: no scene item. 1 and above: matches the node with id "AK<sceneItemId>" in the .dae)
            byte type
                1: geometry
                2: camera
                3: light
                4: text
                5: material
                6: texture
                7: dummy
                8: contract
            byte flags
                1: initially active
                4: is large element (can own slides and be animated)

            if flags & 4:
                byte ignored = 2
                int animationTimePeriod (unused)

            int numAttributes
            Attribute[numAttributes]
                int typeAndName
                int value

                Bits 0..26 of typeAndName: hash of attribute name. Can be one of these:
                    _AKIsContract
                    _AKContractClass
                    AKCustomObjType
                    BehaviorScripts   (Attribute value is a script file name (.xpl))
                    active
                    ambient.a
                    ambient.b
                    ambient.g
                    ambient.r
                    backcolor.a
                    backcolor.b
                    backcolor.g
                    backcolor.r
                    boxheight
                    boxwidth
                    brightness
                    clipfar
                    clipnear
                    diffuse.a
                    diffuse.b
                    diffuse.g
                    diffuse.r
                    emissivepower
                    endtime
                    expfade
                    fogcolor.a
                    fogcolor.b
                    fogcolor.g
                    fogcolor.r
                    fogenable
                    fogfar
                    fognear
                    font
                    fov
                    globalactive
                    horzalign
                    horzscroll
                    layercolor.r
                    layerheight
                    layerwidth
                    leading
                    lightambient.a
                    lightambient.b
                    lightambient.g
                    lightambient.r
                    lightdiffuse.a
                    lightdiffuse.b
                    lightdiffuse.g
                    lightdiffuse.r
                    lightspecular.a
                    lightspecular.b
                    lightspecular.g
                    lightspecular.r
                    linearfade
                    mousepicking
                    name
                    opacity
                    orientation
                    orthographic
                    outerconeangle
                    parent
                    pivot.x
                    pivot.y
                    pivot.z
                    pivotu
                    pivotv
                    position.x
                    position.y
                    position.z
                    positionu
                    positionv
                    renderbehindcockpit
                    rendergroupidentifier
                    renderpriority
                    renderstyle
                    rendertarget
                    rotation.x
                    rotation.y
                    rotation.z
                    rotationorder
                    rotationuv
                    scale.x
                    scale.y
                    scale.z
                    scaleu
                    scalev
                    size
                    source
                    specular.a
                    specular.b
                    specular.g
                    specular.r
                    specularenable
                    specularpower
                    textcolor.a
                    textcolor.b
                    textcolor.g
                    textcolor.r
                    textstring
                    texttype
                    tilingmodehorz
                    tilingmodevert
                    timeoffset
                    tracking
                    transparent
                    usebackcolor
                    vertalign
                    vertscroll
                    wordwrap

                Bits 27..29 of typeAndName: data type of the "value" field
                    1: int
                    3: float
                    4: bool
                    5: 0-based integer index into strings section

    contracts section (unused?)
        int sectionSize
        Contract[memory.counts[3]]
            int elementIdx
            int numEvents
            int eventNameStringIndices[numEvents]

    animations section
        int sectionSize
        Animation[memory.counts[8]]
            int elementIdx
            int attrNameHash (see list of attribute names in elements section)
            byte bEnabled
            byte bCanSyncFirstKeyframe
            short numKeyframes
            Keyframe[numKeyframes]
                int   timeOffset
                float bezierP0
                float ?spline1 = 0
                float bezierP1
                float ?spline2 = 0
                float bezierP2

    logic section (never occurs in XR)
        int sectionSize
        ...

    params section
        int sectionSize
        Param[memory.counts[13]]
            int typeHash
                Hash of one of the following:
                "float"
                "float3.x", "float3.y", "float3.z"
                "long"
                "color4.r", "color4.g", "color4.b", "color4.a"
                "bool"
                "string"
            int value
                For float, float3.?, long: a float
                For color4.?: a float 0-255
                For bool: 0 or 1
                For string: a string index

    slides section
        int sectionSize
        Slide[memory.counts[14]]
            char szName[0x10]
            int elementIdx
            byte flags
                0-1: period factor
                2: 0 -> initially paused, 1 -> initially playing
                3: 0 -> time is reset to period after period*periodFactor, 1 -> time is reset to 0 after period
                4: ?
            int beginTimeMs
            int endTimeMs    (endTimeMs - beginTimeMs = animation period)
            int numElemSettings
            ElementSetting[numElemSettings]
                int elementIdx
                byte bActivate
                int numAttributeValues
                AttributeValue[numAttributes]
                    int typeAndName
                    int value

                int numAnimOrLogicRefs
                AnimOrLogicRef[numAnimOrLogicRefs]
                    byte bIsLogic = 0
                    byte bEnable
                    short animOrLogicIdx

.bsg (Binary Scene Graph):
    header
        byte endianness = 0
        byte ignored = 4
        short ignored = 0
        int headerSize = 0x18
        byte magic[8] = "AnarkBGF"
        int version = 2
        int ignored = 2
        byte ignored[8]

    memory section
        int sectionSize = 8
        int numNodes
        int numAssets

    scene graph section
        int sectionSize
        GraphNode[memory.numNodes]
            int parentNodeIdx (index into the GraphNode array; -1 for root nodes)
            int sceneNodeId (e.g. 130 -> matches node "AK130" in the .dae)
            byte type
                1: dummy
                2: geometry
                3: camera
                4: light
                5: text
                8: layer
            byte ignored[3]
            Vec3D translation (negated Z)
            Vec3D rotation (euclidian, radians; negated X and Y)
            Vec3D scale
            Vec3D rotatePivot (negated Z)
            Vec3D boundingBoxMinPos
            Vec3D boundingBoxMaxPos
            float localOpacity
            byte layerIdx (0..7)
            byte rotationMethod = 4
            byte bInvertY
            int unused = 0
            byte bTransparent

    assets section
        int sectionSize
        Asset[memory.numAssets]
            int sceneNodeId
            byte type
                6: material
                7: texture
```
