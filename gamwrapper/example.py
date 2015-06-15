from gamwrapper import GamWrapper

if __name__ == "__main__":
	gw = GamWrapper(verbose=True)
	gw.call_gam('gam hi "there dude"')
	gw.call_gam('gam another one')