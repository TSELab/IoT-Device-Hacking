import docker
import os #, tarfile for some reason is not liking symlinks

client = None

def initDocker():
	global client
	client = docker.from_env()
	if(client):
		return True
	return False

def saveContainer(container, fname):
	if(container):
		outStream = container.export();
		with open("out.tar", "wb") as f:
			for chunk in outStream:
				f.write(chunk)
		if not os.path.exists(fname):
			os.mkdir(fname)
		#with tarfile.open("out.tar") as tar:
		#	tar.extractall(path=f"./{fname}")
		os.system(f"tar -xf out.tar -C {fname}")
		os.remove("out.tar");

def pullXtractImage(imgName, fname):
	if(client):
		img = client.images.pull(imgName)
		if(img):
			container = client.containers.create(img)
			if(container):
				saveContainer(container, fname)
				container.remove()
			else:
				print("Unable to create container")
			img.remove()

if __name__ == "__main__":
	initDocker()
	pullXtractImage("busybox", "test")
