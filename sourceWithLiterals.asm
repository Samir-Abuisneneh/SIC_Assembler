COPY     START  1000               COMMENT
FIRST    STL    RETADR             COMMENT
CLOOP    JSUB   RDREC              
         LDA    LENGTH             COMMENTCOMMENTCOMMENTCOMMENTCOMMENT
         COMP   ZERO               COMMENTCOMMENT
         JEQ    ENDFIL             
         JSUB   WRREC              COMMENTCOMMENT
         J      CLOOP              
ENDFIL   LDA    =C'EOF'                
         STA    BUFFER             COMMENT
         LDA    THREE              
         STA    LENGTH             
         JSUB   WRREC              COMMENT
         LTORG
         LDL    RETADR             
         RSUB                      
EOF      BYTE   C'EOF'             
THREE    WORD   3                  
ZERO     WORD   0                  
RETADR   RESW   1                  COMMENTCOMMENTCOMMENT
LENGTH   RESW   1                  
BUFFER   RESB   4096               
.               
.        SUBROUTINE TO READ RECORD INTO BUFFER
.                
RDREC    LDX    ZERO               
         LDA    ZERO               COMMENT
RLOOP    TD     INPUT              
         JEQ    RLOOP              
         RD     INPUT              COMMENTCOMMENTCOMMENT
         COMP   ZERO               
         JEQ    EXIT               
         STCH   BUFFER,X           
         TIX    MAXLEN             
         JLT    RLOOP              
EXIT     STX    LENGTH             
         RSUB                      
INPUT    BYTE   X'F1'              
MAXLEN   WORD   4096               
.                
.        SUBROUTINE TO WRITE RECORD FROM BUFFER
.               
WRREC    LDX    ZERO               
WLOOP    TD     =X'05'             
         JEQ    WLOOP              
         LDCH   BUFFER,X           
         WD     =X'05'             
         TIX    LENGTH             
         JLT    WLOOP              
         RSUB                      
OUTPUT   BYTE   X'05'              
         END    FIRST