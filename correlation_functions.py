import numpy as np


def adjustdims(arr1, arr2):
    """Given two arrays, pads the smallest one to the dimensions of the bigest ones.
    inputs:
        - arr1: input 1 np.ndarray
        - arr2: input 2 np.ndarray
    outputs:
        - arrays 1 and to padded to the dimensions of the bigger ones."""
    dx1 = np.shape(arr1)[1]
    dy1 = np.shape(arr1)[0]
    dx2 = np.shape(arr2)[1]
    dy2 = np.shape(arr2)[0]
    dx = max(dx1, dx2)
    dy = max(dy1, dy2)
    return centerpad(arr1, (dy, dx)), centerpad(arr2, (dy, dx))


def centerpad(arr, dims, constval=0, mode=0):
    """Centers an array to the specified dimensions."""
    dx = np.shape(arr)[1]
    dy = np.shape(arr)[0]
    if mode == 1:
        nx = np.shape(dims)[1]
        ny = np.shape(dims)[0]
    else:
        nx = dims[1]
        ny = dims[0]
    if dx >= nx: nx = dx
    if dy >= ny: ny = dy
    xl = np.int(np.ceil((nx - dx) / 2))
    xr = nx - dx - xl
    yl = np.int(np.ceil((ny - dy) / 2))
    yr = ny - dy - yl
    return np.pad(arr, ((yl, yr), (xl, xr)), 'constant', constant_values=((constval, constval), (constval, constval)))


def correlate(arr1, arr2, extrashift=1, maximum=False):
    """Correlate two images:
    input:
        - arr1: np.ndarray
            First array to consider
        - arr2: np.ndarray
            Second array to consider
        - extrashift: bool
            True if an extra shift is wanted in the last inverse FFT
        - maximum: bool
            if True,  returns the maximum value of the correlation array.
            if False, returns the correlation array
    output:
        - correlation or correlation maximum,
            depending on the value of 'maximum'."""
    arr1, arr2 = adjustdims(arr1, arr2)
    tfcorr = (fft(arr1).conj() * fft(arr2))
    correlation = fft(tfcorr / (np.abs(tfcorr) + 1e-20), -2, extrashift)
    if not maximum: return correlation
    if maximum: return np.max(correlation)


def fft(imor, mode=1, extrashift=0):
    """Fast Fourier Transform operacions relacionades, amb correccions de shift, en una o dues dimensions
    depenent de si hi introduïm array de una o dues dimensions.
    inputs:
        - imor: np.ndarray
            original image
        - mode: can be:
             1: FFT
            -1: iFFT
             2: Modul(FFT)
            -2: Modul(iFFT)
             3: Fase(FFT)
            -3: Fase(iFFT)
             4: Real(FFT)
            -4: Real(iFFT)
             5: Imag(FFT)
            -5: Imag(iFFT)
        - extrashift: bool
            True if an extra shift is desired."""
    imin = np.copy(imor)
    dim = len(np.shape(imin))
    modedict = dict(fft2=1, ifft2=-1, fft2_module=2, ifft2_module=-2, fft2_phase=3)
    if type(mode) == str and str in modedict:
        mode = modedict[mode]
    if dim == 2:
        if mode == 1:
            outp = np.fft.fftshift(np.fft.fft2(imin))
        elif mode == 2:
            outp = np.abs(np.fft.fftshift(np.fft.fft2(imin)))
        elif mode == 3:
            outp = np.angle(np.fft.fftshift(np.fft.fft2(imin)))
        elif mode == -1:
            outp = np.fft.ifft2(np.fft.ifftshift(imin))
        elif mode == -2:
            outp = np.abs(np.fft.ifft2(np.fft.ifftshift(imin)))
        elif mode == -3:
            outp = np.angle(np.fft.ifft2(np.fft.ifftshift(imin)))
    elif dim == 1:
        if mode == 1:
            outp = np.fft.fftshift(np.fft.fft(imin))
        elif mode == 2:
            outp = np.abs(np.fft.fftshift(np.fft.fft(imin)))
        elif mode == 3:
            outp = np.angle(np.fft.fftshift(np.fft.fft(imin)))
        elif mode == -1:
            outp = np.fft.ifft(np.fft.ifftshift(imin))
        elif mode == -2:
            outp = np.abs(np.fft.ifft(np.fft.ifftshift(imin)))
        elif mode == -3:
            outp = np.angle(np.fft.ifft(np.fft.ifftshift(imin)))

    if extrashift == 1:
        outp = np.fft.ifftshift(outp)

    return outp


def binarize(img):
    '''A function that blurs and binarizes (inverse mode, so black background) the input
    inputs:
        - img: np.ndarray
            input image
    outpus:
        - th: np.ndarray
            thresholded image'''

    blur = np.copy(img)

    # The image is first blurred
    for i in range(10):
        blur = cv2.GaussianBlur(blur, (5, 5), 0)

    # The thresholding is applied
    # Note: a global thresholding is chosen over adaptive thresholding because, as the strokes (black areas in the
    # original image) might (actually, should) be thick, whereas the background should be uniform, highly varying
    # thresholds might be incorrectly chosen. It is also chosen over Otsu binarization because of the control that
    # the user has in tuning the optimal threshold value. Actually, Otsu usually returns background areas recognized
    # as stroke. Thus, the image should contain nothing but the kanji, as big as possible, and the illumination
    # should be as constant as possible for a correct binarization.
    th = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)[1]
    # A closing fills in holes.
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=1)
    # An opening removes white chunks.
    th = cv2.morphologyEx(th, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), iterations=1)
    # An erosion facilitates the image processing
    th = cv2.erode(th, np.ones((3, 3), np.uint8), iterations=2)
    return th
