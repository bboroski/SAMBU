using System;
using UnityEngine;
using UnityEngine.Rendering;

namespace Sambu.Voxels
{
    /// <summary>
    /// Applies a SAMBU surface-mesh payload to a Unity MeshFilter.
    /// Coordinates are voxel-grid-local; apply the SAMBU frame transform to the GameObject.
    /// </summary>
    public static class SambuVoxelBridge
    {
        public static Mesh Apply(
            MeshFilter target,
            Vector3[] vertices,
            Vector3[] normals,
            int[] indices,
            string meshName = "SAMBU Voxel Chunk")
        {
            if (target == null) throw new ArgumentNullException(nameof(target));
            if (vertices == null || indices == null) throw new ArgumentNullException("Mesh arrays cannot be null.");
            if (indices.Length % 3 != 0) throw new ArgumentException("Triangle index count must be divisible by three.");
            if (normals != null && normals.Length != vertices.Length)
                throw new ArgumentException("Normals must match the vertex count.");

            var mesh = new Mesh { name = meshName };
            if (vertices.Length > 65535) mesh.indexFormat = IndexFormat.UInt32;
            mesh.vertices = vertices;
            if (normals != null && normals.Length == vertices.Length) mesh.normals = normals;
            else mesh.RecalculateNormals();
            mesh.SetTriangles(indices, 0, true);
            mesh.RecalculateBounds();

            var previous = target.sharedMesh;
            target.sharedMesh = mesh;
            if (previous != null && Application.isPlaying) UnityEngine.Object.Destroy(previous);
            return mesh;
        }

        public static GraphicsBuffer CreateVoxelBuffer(byte[] packedCells, int cellCount)
        {
            if (packedCells == null) throw new ArgumentNullException(nameof(packedCells));
            const int stride = 5; // local x/y/z uint8 + material uint16, little-endian
            if (cellCount < 0 || packedCells.Length != cellCount * stride)
                throw new ArgumentException("Packed voxel payload length does not match cellCount.");
            var buffer = new GraphicsBuffer(GraphicsBuffer.Target.Structured, Math.Max(1, cellCount), stride);
            if (cellCount > 0) buffer.SetData(packedCells);
            return buffer;
        }
    }
}
