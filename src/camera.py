from picamera import PiCamera

camera = PiCamera()
camera.resolution = (3280, 2464)

def take_picture(name:str) -> None:
	camera.capture(name)
