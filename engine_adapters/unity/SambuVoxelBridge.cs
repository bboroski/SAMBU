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
            const int packedStride = 5; // SAMBU transfer format
            const int gpuStride = 8;    // two uint32 words; compatible structured-buffer alignment
            if (cellCount < 0 || packedCells.Length != cellCount * packedStride)
                throw new ArgumentException("Packed voxel payload length does not match cellCount.");
            var gpuWords = new uint[cellCount * 2];
            for (int i = 0; i < cellCount; i++)
            {
                int source = i * packedStride;
                uint packedCoordinate = (uint)(packedCells[source]
                    | (packedCells[source + 1] << 8)
                    | (packedCells[source + 2] << 16));
                uint material = (uint)(packedCells[source + 3] | (packedCells[source + 4] << 8));
                gpuWords[i * 2] = packedCoordinate;
                gpuWords[i * 2 + 1] = material;
            }
            var buffer = new GraphicsBuffer(GraphicsBuffer.Target.Structured, Math.Max(1, cellCount), gpuStride);
            if (cellCount > 0) buffer.SetData(gpuWords);
            return buffer;
        }
    }
}
