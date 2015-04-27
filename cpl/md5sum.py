import hashlib

def datamd5(hdulist):
    '''Calculate the MD5SUM of all data regions of a HDUList.
    '''
    md5sum = hashlib.md5()
    for hdu in hdulist:
        if hdu.data is not None:
            md5sum.update(bytes(hdu.data.data))
            pad = b'\0' * (2880 - hdu.data.nbytes % 2880)
            md5sum.update(pad)
    return md5sum.hexdigest()

def verify_md5(hdulist):
    return hdulist[0].header.get('DATAMD5') == datamd5(hdulist)

def update_md5(hdulist):
    md5sum = datamd5(hdulist)
    hdulist[0].header['DATAMD5'] =  (md5sum, 'MD5 checksum')
    return md5sum
