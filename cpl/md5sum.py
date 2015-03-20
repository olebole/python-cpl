import os 
import hashlib

def datamd5(hdulist):
    '''Calculate the MD5SUM of all data regions of a HDUList.
    '''
    sum = hashlib.md5()
    for hdu in hdulist:
        if hdu.data is not None:
            sum.update(bytes(hdu.data.data))
            pad = b'\0' * (2880 - hdu.data.nbytes % 2880)
            sum.update(pad)
    return sum.hexdigest()

def verify_md5(hdulist):
    return hdulist[0].header.get('DATAMD5') == datamd5(hdulist)

def update_md5(hdulist):
    sum = datamd5(hdulist)
    hdulist[0].header['DATAMD5'] =  (sum, 'MD5 checksum')
    return sum
