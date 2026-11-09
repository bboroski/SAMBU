#include "SambuVoxelBridge.h"

void USambuVoxelBridge::ApplySurfaceMesh(
    const TArray<FVector>& Vertices,
    const TArray<FVector>& Normals,
    const TArray<int32>& Triangles,
    int32 SectionIndex,
    bool bCreateCollision)
{
    if (Triangles.Num() % 3 != 0)
    {
        UE_LOG(LogTemp, Error, TEXT("SAMBU voxel mesh: index count must be divisible by three."));
        return;
    }
    if (Normals.Num() != 0 && Normals.Num() != Vertices.Num())
    {
        UE_LOG(LogTemp, Error, TEXT("SAMBU voxel mesh: normals must match vertex count."));
        return;
    }
    for (const int32 Index : Triangles)
    {
        if (!Vertices.IsValidIndex(Index))
        {
            UE_LOG(LogTemp, Error, TEXT("SAMBU voxel mesh: index outside vertex array."));
            return;
        }
    }

    TArray<FVector2D> UV0;
    TArray<FLinearColor> Colors;
    TArray<FProcMeshTangent> Tangents;
    UV0.Init(FVector2D::ZeroVector, Vertices.Num());
    Colors.Init(FLinearColor::White, Vertices.Num());
    Tangents.Init(FProcMeshTangent(), Vertices.Num());

    CreateMeshSection_LinearColor(
        SectionIndex, Vertices, Triangles, Normals, UV0, Colors, Tangents,
        bCreateCollision);
}
