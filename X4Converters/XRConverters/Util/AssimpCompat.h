#pragma once

#include <assimp/scene.h>
#include <vector>

namespace AssimpCompat
{
    void SetIsBone(aiNode* node, bool isBone);
    bool IsBone(aiNode* node);

    // Compute world transformation matrix for a node
    aiMatrix4x4 GetWorldTransformation(aiNode* node);

    // Deep-clone a mesh (used to create deformed/morph meshes)
    aiMesh* CloneMesh(const aiMesh* src);

    // Morph-target bookkeeping
    void AddMorphTarget(aiMesh* base, aiMesh* morph);
    std::vector<aiMesh*> GetMorphTargets(aiMesh* base);
}
