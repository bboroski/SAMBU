extends Node3D
class_name SambuVoxelBridge
## Applies SAMBU voxel surface arrays to a Godot ArrayMesh.
## Vertex coordinates are voxel-grid-local. Apply the SAMBU frame to this Node3D.

@export var surface_instance: MeshInstance3D

func apply_surface_mesh(
        vertices: PackedVector3Array,
        normals: PackedVector3Array,
        indices: PackedInt32Array
) -> ArrayMesh:
    if surface_instance == null:
        push_error("SAMBU: surface_instance is not assigned.")
        return null
    if indices.size() % 3 != 0:
        push_error("SAMBU: index count must be divisible by three.")
        return null
    if not normals.is_empty() and normals.size() != vertices.size():
        push_error("SAMBU: normals must match vertex count.")
        return null

    var arrays := []
    arrays.resize(Mesh.ARRAY_MAX)
    arrays[Mesh.ARRAY_VERTEX] = vertices
    arrays[Mesh.ARRAY_INDEX] = indices
    if normals.size() == vertices.size():
        arrays[Mesh.ARRAY_NORMAL] = normals

    var mesh := ArrayMesh.new()
    var error := mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
    if error != OK:
        push_error("SAMBU: Godot failed to create ArrayMesh surface: %s" % error)
        return null
    surface_instance.mesh = mesh
    return mesh

func supports_gpu_voxel_compute() -> bool:
    # RenderingDevice is unavailable in headless and Compatibility rendering modes.
    return RenderingServer.get_rendering_device() != null
