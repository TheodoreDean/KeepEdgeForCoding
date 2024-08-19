#ifndef _DLL_H_
#define _DLL_H_

/*
extern "C" int GenerateKeyEx(
    const unsigned char* iSeedArray, 
    unsigned short iSeedArraySize,
    const unsigned int iSecurityLevel, 
    const char* iVariant,
    unsigned char* ioKeyArray,
    unsigned int iKeyArraySize,
    unsigned int& oSize
);
*/
extern "C" int ZLGKey(
    const unsigned char*    iSeedArray,        // seed����
    unsigned short          iSeedArraySize,    // seed�����С
    unsigned int            iSecurityLevel,    // ��ȫ���� 1,3,5...
    const char*             iVariant,          // ��������, ������Ϊ��
    unsigned char*          iKeyArray,         // key����, �ռ����û�����
    unsigned short*         iKeyArraySize      // key�����С, ��������ʱΪkey����ʵ�ʴ�С
);

#endif
