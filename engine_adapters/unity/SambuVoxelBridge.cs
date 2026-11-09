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

        /// <summary>
        /// Dispatches count -> group-prefix-scan -> face emission. Output buffers must
        /// have capacity for the worst case of six exposed faces per input voxel.
        /// All compute dispatches stay on the GPU; no synchronous readback is performed.
        /// </summary>
        public static int DispatchCompactVoxelMesher(
            ComputeShader shader,
            int cellCount,
            GraphicsBuffer cells,
            GraphicsBuffer faceMasks,
            GraphicsBuffer groupFaceCounts,
            GraphicsBuffer groupFaceOffsets,
            GraphicsBuffer totalFaceCount,
            GraphicsBuffer vertices,
            GraphicsBuffer normals,
            GraphicsBuffer indices,
            GraphicsBuffer faceMaterials,
            GraphicsBuffer drawIndexedArgs)
        {
            if (shader == null) throw new ArgumentNullException(nameof(shader));
            if (cellCount < 0) throw new ArgumentOutOfRangeException(nameof(cellCount));
            if (cells == null || faceMasks == null || groupFaceCounts == null ||
                groupFaceOffsets == null || totalFaceCount == null ||
                vertices == null || normals == null || indices == null ||
                faceMaterials == null || drawIndexedArgs == null)
                throw new ArgumentNullException("All SAMBU voxel compute buffers are required.");

            const int threadsPerGroup = 64;
            int groupCount = (cellCount + threadsPerGroup - 1) / threadsPerGroup;
            long maxFaces = (long)cellCount * 6L;

            if (cells.count < cellCount || faceMasks.count < cellCount)
                throw new ArgumentException("Input cell and face-mask buffers are too small.");
            if (groupFaceCounts.count < groupCount || groupFaceOffsets.count < groupCount)
                throw new ArgumentException("Group scan buffers are too small.");
            if (totalFaceCount.count < 1 || drawIndexedArgs.count < 5)
                throw new ArgumentException("Total-face and indirect-argument buffers are too small.");
            if (vertices.count < maxFaces * 4L || normals.count < maxFaces * 4L ||
                indices.count < maxFaces * 6L || faceMaterials.count < maxFaces)
                throw new ArgumentException("Output buffers must fit the worst-case six faces per voxel.");

            if (cellCount == 0)
            {
                totalFaceCount.SetData(new uint[] { 0u });
                drawIndexedArgs.SetData(new uint[] { 0u, 1u, 0u, 0u, 0u });
                return 0;
            }

            int countKernel = shader.FindKernel("CountVisibleFaces");
            int scanKernel = shader.FindKernel("ScanGroupOffsets");
            int emitKernel = shader.FindKernel("EmitVisibleFaces");

            shader.SetInt("_CellCount", cellCount);
            shader.SetInt("_GroupCount", groupCount);

            shader.SetBuffer(countKernel, "_Cells", cells);
            shader.SetBuffer(countKernel, "_FaceMasks", faceMasks);
            shader.SetBuffer(countKernel, "_GroupFaceCounts", groupFaceCounts);

            shader.SetBuffer(scanKernel, "_GroupFaceCounts", groupFaceCounts);
            shader.SetBuffer(scanKernel, "_GroupFaceOffsets", groupFaceOffsets);
            shader.SetBuffer(scanKernel, "_TotalFaceCount", totalFaceCount);
            shader.SetBuffer(scanKernel, "_DrawIndexedArgs", drawIndexedArgs);

            shader.SetBuffer(emitKernel, "_Cells", cells);
            shader.SetBuffer(emitKernel, "_FaceMasks", faceMasks);
            shader.SetBuffer(emitKernel, "_GroupFaceOffsets", groupFaceOffsets);
            shader.SetBuffer(emitKernel, "_Vertices", vertices);
            shader.SetBuffer(emitKernel, "_Normals", normals);
            shader.SetBuffer(emitKernel, "_Indices", indices);
            shader.SetBuffer(emitKernel, "_FaceMaterials", faceMaterials);

            // Ordered dispatches on the same graphics queue establish the required
            // UAV dependencies between count, scan and emit stages.
            shader.Dispatch(countKernel, groupCount, 1, 1);
            shader.Dispatch(scanKernel, 1, 1, 1);
            shader.Dispatch(emitKernel, groupCount, 1, 1);
            return groupCount;
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
