const CryptoJS = require("crypto-js");

function encryptWithAES(passphrase, text) {
    return CryptoJS.AES.encrypt(text, passphrase).toString();
}

function decryptWithAES(passphrase, ciphertext) {
    if (ciphertext) {
        const bytes = CryptoJS.AES.decrypt(ciphertext, passphrase);
        return bytes.toString(CryptoJS.enc.Utf8);
    } else {
        return null;
    }
}

function getPassphraseFromEnv() {
    return process.env.PASSPHRASE;
}

module.exports = {
    encryptWithAES,
    decryptWithAES,
    getPassphraseFromEnv
};

