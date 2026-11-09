#pragma once

#include "CoreMinimal.h"
#include "ProceduralMeshComponent.h"
#include "SambuVoxelBridge.generated.h"

/**
 * Runtime bridge for SAMBU chunk surface meshes.
 * Enable the ProceduralMeshComponent plugin in the host .uproject.
 */
UCLASS(ClassGroup=(Rendering), meta=(BlueprintSpawnableComponent))
class USambuVoxelBridge : public UProceduralMeshComponent
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="SAMBU|Voxels")
    void ApplySurfaceMesh(
        const TArray<FVector>& Vertices,
        const TArray<FVector>& Normals,
        const TArray<int32>& Triangles,
        int32 SectionIndex = 0,
        bool bCreateCollision = false);
};
