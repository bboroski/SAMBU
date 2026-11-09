#pragma once

#include <AzCore/Math/Vector3.h>
#include <AzCore/Math/Matrix3x3.h>
#include <AzCore/Math/Transform.h>
#include <AzCore/std/containers/vector.h>
#include <AzCore/std/containers/array.h>
#include <AzCore/std/containers/span.h>

namespace Sambu::Voxels
{
    struct Vertex
    {
        AZ::Vector3 position = AZ::Vector3::CreateZero();
        AZ::Vector3 normal = AZ::Vector3::CreateAxisZ();
        AZStd::array<float, 2> uv{0.0f, 0.0f};
        AZ::u16 materialId = 1;
    };

    struct MeshData
    {
        AZStd::vector<Vertex> vertices;
        AZStd::vector<AZ::u32> indices;
        AZStd::vector<AZ::u16> faceMaterials;
    };

    /// Convert voxel-grid-local mesh arrays into an Atom FeatureProcessor-ready payload.
    /// The owning O3DE Gem should upload these arrays through its RPI/RHI lifecycle.
    inline bool Validate(const MeshData& mesh)
    {
        if (mesh.indices.size() % 3 != 0)
            return false;
        if (mesh.indices.empty() != mesh.vertices.empty())
            return false;
        for (AZ::u32 index : mesh.indices)
            if (index >= mesh.vertices.size())
                return false;
        return true;
    }

    inline AZ::Vector3 GridToWorld(
        const AZ::Vector3& cellPosition,
        const AZ::Vector3& origin,
        const AZ::Matrix3x3& axes,
        float voxelSize)
    {
        return origin + (axes * cellPosition) * voxelSize;
    }
}
