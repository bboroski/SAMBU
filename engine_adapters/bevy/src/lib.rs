//! Bevy 0.20.1 mesh bridge for SAMBU voxel surface payloads.
//! The host applies the SAMBU VoxelFrame to the spawned entity transform.

use bevy::asset::RenderAssetUsages;
use bevy::mesh::{Indices, Mesh, PrimitiveTopology};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SambuVoxelError {
    IndexCountNotTriangular,
    NormalCountMismatch,
    IndexOutOfBounds,
}

pub fn mesh_from_arrays(
    vertices: &[[f32; 3]],
    normals: &[[f32; 3]],
    indices: &[u32],
) -> Result<Mesh, SambuVoxelError> {
    if indices.len() % 3 != 0 {
        return Err(SambuVoxelError::IndexCountNotTriangular);
    }
    if !normals.is_empty() && normals.len() != vertices.len() {
        return Err(SambuVoxelError::NormalCountMismatch);
    }
    if indices.iter().any(|index| *index as usize >= vertices.len()) {
        return Err(SambuVoxelError::IndexOutOfBounds);
    }

    let mut mesh = Mesh::new(
        PrimitiveTopology::TriangleList,
        RenderAssetUsages::default(),
    )
    .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, vertices.to_vec());

    if normals.len() == vertices.len() {
        mesh.insert_attribute(Mesh::ATTRIBUTE_NORMAL, normals.to_vec());
    }

    mesh.insert_indices(Indices::U32(indices.to_vec()));
    Ok(mesh)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_indices_outside_vertex_array() {
        assert_eq!(
            mesh_from_arrays(&[[0.0, 0.0, 0.0]], &[], &[0, 1, 2]).unwrap_err(),
            SambuVoxelError::IndexOutOfBounds,
        );
    }

    #[test]
    fn rejects_non_triangular_index_count() {
        assert_eq!(
            mesh_from_arrays(&[], &[], &[0, 1]).unwrap_err(),
            SambuVoxelError::IndexCountNotTriangular,
        );
    }

    #[test]
    fn builds_triangle_mesh() {
        let mesh = mesh_from_arrays(
            &[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            &[[0.0, 0.0, 1.0]; 3],
            &[0, 1, 2],
        ).unwrap();
        assert_eq!(mesh.count_vertices(), 3);
    }
}
