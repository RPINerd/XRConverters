#include "AssimpCompat.h"
#include "StdInc.h"

namespace AssimpCompat
{
    // keep in-process maps to store compatibility metadata that isn't present on aiNode/aiMesh
    static std::unordered_map<aiNode*, bool> s_isBoneMap;
    static std::unordered_map<aiMesh*, std::vector<aiMesh*>> s_morphMap;

    void SetIsBone(aiNode* node, bool isBone)
    {
        if (!node) return;
        s_isBoneMap[node] = isBone;
    }

    bool IsBone(aiNode* node)
    {
        if (!node) return false;
        auto it = s_isBoneMap.find(node);
        if (it == s_isBoneMap.end()) return false;
        return it->second;
    }

    aiMatrix4x4 GetWorldTransformation(aiNode* node)
    {
        aiMatrix4x4 mat;
        if (!node) return mat;
        mat = node->mTransformation;
        aiNode* cur = node->mParent;
        while (cur)
        {
            mat = cur->mTransformation * mat;
            cur = cur->mParent;
        }
        return mat;
    }

    aiMesh* CloneMesh(const aiMesh* src)
    {
        if (!src) return nullptr;
        aiMesh* m = new aiMesh();
        *m = *src; // shallow copy
        if (src->mNumVertices && src->mVertices)
        {
            m->mVertices = new aiVector3D[src->mNumVertices];
            for (unsigned i=0;i<src->mNumVertices;++i) m->mVertices[i] = src->mVertices[i];
        }
        if (src->mNormals)
        {
            m->mNormals = new aiVector3D[src->mNumVertices];
            for (unsigned i=0;i<src->mNumVertices;++i) m->mNormals[i] = src->mNormals[i];
        }
        if (src->mTangents)
        {
            m->mTangents = new aiVector3D[src->mNumVertices];
            for (unsigned i=0;i<src->mNumVertices;++i) m->mTangents[i] = src->mTangents[i];
        }
        if (src->mBitangents)
        {
            m->mBitangents = new aiVector3D[src->mNumVertices];
            for (unsigned i=0;i<src->mNumVertices;++i) m->mBitangents[i] = src->mBitangents[i];
        }
        if (src->mNumFaces && src->mFaces)
        {
            m->mNumFaces = src->mNumFaces;
            m->mFaces = new aiFace[m->mNumFaces];
            for (unsigned i=0;i<m->mNumFaces;++i)
            {
                m->mFaces[i].mNumIndices = src->mFaces[i].mNumIndices;
                m->mFaces[i].mIndices = new unsigned int[src->mFaces[i].mNumIndices];
                for (unsigned j=0;j<src->mFaces[i].mNumIndices;++j) m->mFaces[i].mIndices[j] = src->mFaces[i].mIndices[j];
            }
        }
        return m;
    }

    void AddMorphTarget(aiMesh* base, aiMesh* morph)
    {
        if (!base || !morph) return;
        s_morphMap[base].push_back(morph);
    }

    std::vector<aiMesh*> GetMorphTargets(aiMesh* base)
    {
        auto it = s_morphMap.find(base);
        if (it == s_morphMap.end()) return {};
        return it->second;
    }
}
