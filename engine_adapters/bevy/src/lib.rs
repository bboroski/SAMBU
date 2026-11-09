//! Bevy 0.15 mesh bridge for SAMBU voxel surface payloads.
//! The host applies the SAMBU VoxelFrame to the spawned entity transform.

use bevy::asset::RenderAssetUsages;
use bevy::mesh::{Indices, Mesh};
use bevy::render::render_resource::PrimitiveTopology;
use bevy::prelude::Vec3;

#[derive(Debug)]
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

    let positions: Vec<[f32; 3]> = vertices.iter().copied().collect();
    let mut mesh = Mesh::new(
        PrimitiveTopology::TriangleList,
        RenderAssetUsages::default(),
    );
    mesh.insert_attribute(Mesh::ATTRIBUTE_POSITION, positions);
    if normals.len() == vertices.len() {
        let values: Vec<[f32; 3]> = normals.iter().copied().collect();
        mesh.insert_attribute(Mesh::ATTRIBUTE_NORMAL, values);
    } else {
        let values: Vec<Vec3> = vertices.iter().map(|p| Vec3::from_array(*p)).collect();
        let _ = values; // Host may compute normals or use SAMBU-provided face normals.
    }
    mesh.insert_indices(Indices::U32(indices.to_vec()));
    Ok(mesh)
}
