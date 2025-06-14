
# thrid party
import qrcode
import qrcode.image.svg
import numpy as np
import segno
from io import BytesIO
import cv2

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

def matrix_to_platform_blueprint(matrix: np.ndarray, add_border: bool = True) -> str:
    platform = Platform(T="Foundation_1x1")
    space = PlatformSpace()
    
    if add_border:
        matrix = np.pad(matrix, 1, mode='constant', constant_values=0)

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

def content_to_segno_matrix(content: str, version: str = "M1", error_correction_level: str = "L", boost_error: bool = True) -> np.ndarray:
    try:
        qrcode = segno.make(content, version=version, error=error_correction_level, boost_error=boost_error)
    except:
        qrcode = segno.make(content, boost_error=True)
    return np.array(qrcode.matrix)

def content_to_segno_image(content: str, version: str = "M1", error_correction_level: str = "L", boost_error: bool = True) -> tuple[bytes, int, str]:
    """Generate a QR code and return the raw PNG data, version, and error level."""
    try:
        qrcode = segno.make(content, version=version, error=error_correction_level, boost_error=boost_error)
    except:
        qrcode = segno.make(content, boost_error=True)
    
    # Get raw PNG data as bytes
    buffer = BytesIO()
    qrcode.save(buffer, kind='png', scale=10)
    return buffer.getvalue(), qrcode.version, qrcode.error

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


    # for version in range(1, 41):
    #     print("Version: ", version, "Size: ", version_to_size(version))

    # matrix = content_to_segno_matrix("The Beatles", "M1", "L")
    
    # print(print_qr_matrix(matrix))
    # print(matrix.shape)

    # Generate and display QR code
    png_data, version, error_level = content_to_segno_image("The Beatles")
    print(f"QR Code generated - Version: {version}, Error Level: {error_level}")
    
    # Convert PNG data to numpy array and display
    nparr = np.frombuffer(png_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is not None:
        cv2.imshow("QR Code", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Error: Could not decode image data")