#pragma once

#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include <unordered_map>
#include <map>
#include <regex>
#include <set>
#include <string>
#include <vector>

typedef unsigned char   byte;
typedef unsigned short  word;
typedef unsigned int    dword;

typedef unsigned short  ushort;
typedef unsigned int    uint;
typedef unsigned long   ulong;

#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/range.hpp>

#define foreach BOOST_FOREACH

// Use system-installed Assimp headers when available. The CMakeLists sets include
// directories to point at either the system Assimp or the bundled Vendor/assimp.
#include <assimp/ai_assert.h>
#include <assimp/IOStream.hpp>
#include <assimp/IOSystem.hpp>
#include <assimp/ProgressHandler.hpp>
#include <assimp/importerdesc.h>
#include <assimp/Importer.hpp>
// Some versions of Assimp declare BaseImporter in a separate header.
// Include BaseImporter.h explicitly to ensure the full definition is
// available for classes that inherit from Assimp::BaseImporter.
#include <assimp/BaseImporter.h>
#include <assimp/Exporter.hpp>
#include <assimp/scene.h>

#if defined(USE_ARCHIVE_HALF)
// Use the archived half.hpp via a relative include to avoid adding the full
// vendor tree to the include path which can cause header conflicts.
#include "../../archive/XRConvertersSrc/Vendor/half/half.hpp"
#else
#include <half/half.hpp>
#endif

#if defined(USE_SYSTEM_PUGIXML)
	// System pugixml may install header as <pugixml.hpp> or <pugi/pugixml.hpp>.
	// Prefer the single-header include which exists on most systems.
	#include <pugixml.hpp>
#else
	// Fallback: archived pugi include (rare). Prefer installing system pugixml.
	#include "../../archive/XRConvertersSrc/Vendor/pugi/pugixml.hpp"
#endif

// zlib/gzip wrappers (Material.cpp uses gz*). If system zlib is present, include
#if defined(USE_SYSTEM_ZLIB)
	#include <zlib.h>
#else
	// The archived vendor tree may contain a compatible zlib; prefer system zlib.
	#include <zlib.h>
#endif

#include "Color8.h"
#include "Color.h"
#include "Vec2D.h"
#include "Vec3D.h"
#include "Vec4D.h"
#include "Quaternion.h"
#include "Matrix44.h"

#include "DirectX.h"
#include "Util/DXUtil.h"
#include "Util/PathUtil.h"
#include "Util/BinaryReader.h"
#include "Util/BinaryWriter.h"
#include "Util/AssimpUtil.h"

#include "Material.h"
#include "MaterialCollection.h"
#include "MaterialLibrary.h"

#include "Xmf/XmfHeader.h"
#include "Xmf/XmfVertexElement.h"
#include "Xmf/XmfMaterial.h"
#include "Xmf/XmfDataBufferDesc.h"
#include "Xmf/XmfDataBuffer.h"
#include "Xmf/XuMeshFile.h"
#include "ComponentPartLod.h"
#include "ComponentPart.h"
#include "Component.h"

#include "Xmf/XmfImporter.h"
#include "Xmf/XmfExporter.h"

#include "EmotionFX.h"
#include "Xac/XacHeader.h"
#include "Xac/XacChunkHeader.h"
#include "Xac/XacMetaDataChunkv2Header.h"
#include "Xac/XacNodeHierarchyChunkv1NodeHeader.h"
#include "Xac/XacMaterialDefinitionChunkv2Header.h"
#include "Xac/XacMaterialDefinitionChunkv2Layer.h"
#include "Xac/XacMaterialTotalsChunkv1.h"
#include "Xac/XacMeshChunkv1Header.h"
#include "Xac/XacMeshChunkv1VertexElement.h"
#include "Xac/XacMeshChunkv1SubMesh.h"
#include "Xac/XacSkinningChunkv3Header.h"
#include "Xac/XacSkinningChunkv3Influence.h"
#include "Xac/XacSkinningChunkv3InfluenceRange.h"
#include "Xac/XacMorphTargetsChunkv1MorphTarget.h"
#include "Xac/XacMorphTargetsChunkv1Deformation.h"
#include "Xac/XacDeformVec3D16.h"
#include "Xac/XacDeformVec3D8.h"
#include "Xac/XacMorphTargetsChunkv1Transformation.h"
#include "Xac/BoneInfluence.h"
#include "Xac/ActorSubMesh.h"
#include "Xac/ActorMesh.h"
#include "Xac/ActorMaterialLayer.h"
#include "Xac/ActorMaterial.h"
#include "Xac/ActorNodeDeformation.h"
#include "Xac/ActorMorphTarget.h"
#include "Xac/ActorNode.h"
#include "Xac/ActorFile.h"

#include "Xac/XacImporter.h"
#include "Xac/XacExporter.h"

#include "dll.h"
