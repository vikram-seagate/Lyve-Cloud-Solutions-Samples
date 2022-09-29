import CryptoJS from "crypto-js";

export function encryptWithAES(passphrase, text) {
    return CryptoJS.AES.encrypt(text, passphrase).toString();
}

export function decryptWithAES(passphrase, ciphertext) {
    if (ciphertext) {
        const bytes = CryptoJS.AES.decrypt(ciphertext, passphrase);
        return bytes.toString(CryptoJS.enc.Utf8);
    } else {
        return null;
    }
}

