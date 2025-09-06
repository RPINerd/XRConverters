// Minimal DirectX compatibility shims for non-Windows builds.
// Provides only the enums and typedefs referenced by DXUtil.cpp and XMF parsing.
#pragma once

#include <cstdint>

using byte = uint8_t;
using ushort = uint16_t;

// Vertex element types (D3DDECLTYPE) used by the project. Values are arbitrary
// as they are only used in switches inside DXUtil; keep them stable.
enum D3DDECLTYPE : int {
	D3DDECLTYPE_FLOAT1 = 0,
	D3DDECLTYPE_FLOAT2 = 1,
	D3DDECLTYPE_FLOAT3 = 2,
	D3DDECLTYPE_FLOAT4 = 3,
	D3DDECLTYPE_D3DCOLOR = 4,
	D3DDECLTYPE_UBYTE4 = 5,
	D3DDECLTYPE_UBYTE4N = 6,
	D3DDECLTYPE_SHORT2 = 7,
	D3DDECLTYPE_SHORT2N = 8,
	D3DDECLTYPE_USHORT2N = 9,
	D3DDECLTYPE_SHORT4 = 10,
	D3DDECLTYPE_SHORT4N = 11,
	D3DDECLTYPE_USHORT4N = 12,
	D3DDECLTYPE_FLOAT16_2 = 13,
	D3DDECLTYPE_FLOAT16_4 = 14,
	D3DDECLTYPE_DEC3N = 15,
	D3DDECLTYPE_UDEC3 = 16,
};

// Other directx enums used elsewhere can be added here as needed.

// Provide a fallback half float type name if project uses half_float::half
#include <half.hpp>
using half = half_float::half;

