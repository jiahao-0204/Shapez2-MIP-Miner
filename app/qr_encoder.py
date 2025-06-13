
# thrid party
import qrcode
import qrcode.image.svg
import numpy as np

# project
from app.blueprint_composer_v2 import Building, Platform, PlatformSpace, BuildingSpace


def matrix_to_building_blueprint(matrix: np.ndarray) -> str:
    building = Building(T="TrashDefaultInternalVariant")
    space = BuildingSpace()

    y_offset = -matrix.shape[0] // 2
    x_offset = -matrix.shape[1] // 2

    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x]:
                space.add_building(building, X=x + x_offset, Y=y + y_offset)

    return space.to_blueprint()

def matrix_to_platform_blueprint(matrix: np.ndarray) -> str:
    platform = Platform(T="Foundation_1x1")
    space = PlatformSpace()
    
    y_offset = -matrix.shape[0] // 2
    x_offset = -matrix.shape[1] // 2

    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            if matrix[y][x] == 0:
                space.add_platform(platform, X=x + x_offset, Y=y + y_offset)

    return space.to_blueprint()



def content_to_qr_matrix(content: str, version: int = 1, error_correction_level: str = "L") -> np.ndarray:
    qr_generator = qrcode.QRCode(
        version=version, 
        error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{error_correction_level.upper()}", qrcode.constants.ERROR_CORRECT_L), 
        border=1
    )
    qr_generator.add_data(content)
    qr_generator.make(fit=True)
    return np.array(qr_generator.get_matrix())

def print_qr_matrix(matrix: np.ndarray) -> None:
    for row in matrix:
        for cell in row:
            if cell:
                print('x', end='')
            else:
                print(' ', end='')
        print()

# constants
base_size = 20
platform_1x1_dimension = base_size - 6 # 14
platform_2x2_dimension = base_size * 2 - 6 # 34
platform_3x3_dimension = base_size * 3 - 6 # 54
vortex_dimension = base_size

def version_to_size(version: int) -> int:
    return version * 4 + 17

if __name__ == "__main__":
    # content = "shapez2-tools.com"
    # qr_generator = qrcode.QRCode(
    #     version=7, 
    #     error_correction=qrcode.constants.ERROR_CORRECT_L, 
    #     border=1
    # )
    # qr_generator.add_data(content)
    # qr_generator.make(fit=True)
    # print(qr_generator.best_fit())
    


    # matrix = content_to_qr_matrix(content, 7)
    # print_qr_matrix(matrix)
    # print(matrix.shape)
    # print(matrix_to_platform_blueprint(matrix))


    for version in range(1, 41):
        print("Version: ", version, "Size: ", version_to_size(version))