         LDA    FIVE
         STA    ALPHA
         LDCH   CHARZ
         STCH   C1          
ENDFIL   LDA    =C'EOF'
         LDA    =X'F1'         
         LTORG
BUFFER   RESB   4096
         LDA    =X'F1'  
.      SUBROUTINE TO READ RECORD INTO BUFFER
ALPHA    RESW   1                 Uninitialized word.
FIVE     WORD   5                 Word initialized to 5.
CHARZ    BYTE   C'Z'              Byte initialized to ’Z’.
C1       RESB   1                 Uninitialized byte
         END    