# Formule Excel exacte și dependențe

Extrase fără modificare. Backtest are 200 de rânduri identice ca structură; aici este afișat rândul 4. JSON include toate cele 3.068 de formule.

## Model_1X2

### E6

```excel
=IF(COUNT(B6:D6)=0,"",SUM(B6:D6))
```

Dependențe: B6:D6, B6:D6

### F6

```excel
=IF(COUNTBLANK(B6:D6)>0,"INPUT",IF(COUNT(B6:D6)<>3,"INVALID",IF(OR(MIN(B6:D6)<0,MAX(B6:D6)>1,ROUND(ABS(SUM(B6:D6)-1),12)>'Parametri'!B31),"INVALID","OK")))
```

Dependențe: B6:D6, B6:D6, B6:D6, B6:D6, B6:D6, 'Parametri'!B31

### J6

```excel
=IF(F6<>"OK","",B6/E6)
```

Dependențe: F6, B6, E6

### K6

```excel
=IF(F6<>"OK","",C6/E6)
```

Dependențe: F6, C6, E6

### L6

```excel
=IF(F6<>"OK","",D6/E6)
```

Dependențe: F6, D6, E6

### E7

```excel
=IF(COUNT(B7:D7)=0,"",SUM(B7:D7))
```

Dependențe: B7:D7, B7:D7

### F7

```excel
=IF(COUNTBLANK(B7:D7)>0,"INPUT",IF(COUNT(B7:D7)<>3,"INVALID",IF(OR(MIN(B7:D7)<0,MAX(B7:D7)>1,ROUND(ABS(SUM(B7:D7)-1),12)>'Parametri'!B31),"INVALID","OK")))
```

Dependențe: B7:D7, B7:D7, B7:D7, B7:D7, B7:D7, 'Parametri'!B31

### J7

```excel
=IF(F7<>"OK","",B7/E7)
```

Dependențe: F7, B7, E7

### K7

```excel
=IF(F7<>"OK","",C7/E7)
```

Dependențe: F7, C7, E7

### L7

```excel
=IF(F7<>"OK","",D7/E7)
```

Dependențe: F7, D7, E7

### B8

```excel
=IF(NOT(ISNUMBER(Input_Meci!B28)),"",Input_Meci!B28)
```

Dependențe: Input_Meci!B28, Input_Meci!B28

### C8

```excel
=IF(NOT(ISNUMBER(Input_Meci!B29)),"",Input_Meci!B29)
```

Dependențe: Input_Meci!B29, Input_Meci!B29

### D8

```excel
=IF(NOT(ISNUMBER(Input_Meci!B30)),"",Input_Meci!B30)
```

Dependențe: Input_Meci!B30, Input_Meci!B30

### E8

```excel
=IF(COUNT(B8:D8)=0,"",SUM(B8:D8))
```

Dependențe: B8:D8, B8:D8

### F8

```excel
=IF(COUNTBLANK(B8:D8)>0,"INPUT",IF(COUNT(B8:D8)<>3,"INVALID",IF(OR(MIN(B8:D8)<0,MAX(B8:D8)>1,ROUND(ABS(SUM(B8:D8)-1),12)>'Parametri'!B31),"INVALID","OK")))
```

Dependențe: B8:D8, B8:D8, B8:D8, B8:D8, B8:D8, 'Parametri'!B31

### J8

```excel
=IF(F8<>"OK","",B8/E8)
```

Dependențe: F8, B8, E8

### K8

```excel
=IF(F8<>"OK","",C8/E8)
```

Dependențe: F8, C8, E8

### L8

```excel
=IF(F8<>"OK","",D8/E8)
```

Dependențe: F8, D8, E8

### B9

```excel
=IF($F$14<>"READY","",'Parametri'!$B$32*J6+'Parametri'!$B$33*J7+'Parametri'!$B$34*J8)
```

Dependențe: $F$14, 'Parametri'!$B$32, J6, 'Parametri'!$B$33, J7, 'Parametri'!$B$34, J8

### C9

```excel
=IF($F$14<>"READY","",'Parametri'!$B$32*K6+'Parametri'!$B$33*K7+'Parametri'!$B$34*K8)
```

Dependențe: $F$14, 'Parametri'!$B$32, K6, 'Parametri'!$B$33, K7, 'Parametri'!$B$34, K8

### D9

```excel
=IF($F$14<>"READY","",'Parametri'!$B$32*L6+'Parametri'!$B$33*L7+'Parametri'!$B$34*L8)
```

Dependențe: $F$14, 'Parametri'!$B$32, L6, 'Parametri'!$B$33, L7, 'Parametri'!$B$34, L8

### E9

```excel
=IF(COUNT(B9:D9)<>3,"",SUM(B9:D9))
```

Dependențe: B9:D9, B9:D9

### F9

```excel
=IF(COUNT(B9:D9)<>3,"INPUT",IF(ROUND(ABS(E9-1),12)<='Parametri'!B31,"OK","INVALID"))
```

Dependențe: B9:D9, E9, 'Parametri'!B31

### B10

```excel
=IF(OR(NOT(ISNUMBER(B9)),$F$9<>"OK"),"",B9/$E$9)
```

Dependențe: B9, $F$9, B9, $E$9

### C10

```excel
=IF(OR(NOT(ISNUMBER(C9)),$F$9<>"OK"),"",C9/$E$9)
```

Dependențe: C9, $F$9, C9, $E$9

### D10

```excel
=IF(OR(NOT(ISNUMBER(D9)),$F$9<>"OK"),"",D9/$E$9)
```

Dependențe: D9, $F$9, D9, $E$9

### E10

```excel
=IF(COUNT(B10:D10)<>3,"",SUM(B10:D10))
```

Dependențe: B10:D10, B10:D10

### F10

```excel
=IF(COUNT(B10:D10)<>3,"INPUT",IF(ROUND(ABS(E10-1),12)<='Parametri'!B31,"OK","INVALID"))
```

Dependențe: B10:D10, E10, 'Parametri'!B31

### F12

```excel
=IF(COUNTIF(F6:F8,"INVALID")>0,"INVALID",IF(COUNTIF(F6:F8,"OK")=3,"READY","INPUT"))
```

Dependențe: F6:F8, F6:F8

### F13

```excel
=IF(OR('Input_Meci'!B4="",'Input_Meci'!C4="",'Input_Meci'!B5="",NOT(ISNUMBER('Input_Meci'!B6)),'Input_Meci'!B7="",'Input_Meci'!B34=""),"INPUT",IF(OR('Input_Meci'!B4='Input_Meci'!C4,AND('Input_Meci'!B7<>"DA",'Input_Meci'!B7<>"NU"),AND('Input_Meci'!B34<>"A",'Input_Meci'!B34<>"B",'Input_Meci'!B34<>"C"),ABS(SUM('Parametri'!B32:B34)-1)>0.000000000001,MIN('Parametri'!B32:B34)<0),"INVALID","READY"))
```

Dependențe: 'Input_Meci'!B4, 'Input_Meci'!C4, 'Input_Meci'!B5, 'Input_Meci'!B6, 'Input_Meci'!B7, 'Input_Meci'!B34, 'Input_Meci'!B4, 'Input_Meci'!C4, 'Input_Meci'!B7, 'Input_Meci'!B7, 'Input_Meci'!B34, 'Input_Meci'!B34, 'Input_Meci'!B34, 'Parametri'!B32:B34, 'Parametri'!B32:B34

### F14

```excel
=IF('Surse_Date'!L15="CRITICAL MISSING","CRITICAL MISSING",IF(OR(F12="INVALID",F13="INVALID",'Surse_Date'!L15="INVALID"),"INVALID",IF(AND(F12="READY",F13="READY",OR('Surse_Date'!L15="READY",'Surse_Date'!L15="CONDITIONAL")),"READY","PENDING")))
```

Dependențe: 'Surse_Date'!L15, F12, F13, 'Surse_Date'!L15, F12, F13, 'Surse_Date'!L15, 'Surse_Date'!L15

## Draw_Risk

### B4

```excel
=IF(NOT(ISNUMBER('Model_1X2'!C10)),"",'Model_1X2'!C10)
```

Dependențe: 'Model_1X2'!C10, 'Model_1X2'!C10

### C4

```excel
='Parametri'!B8
```

Dependențe: 'Parametri'!B8

### D4

```excel
='Parametri'!B9
```

Dependențe: 'Parametri'!B9

### E4

```excel
='P0_Gates_v2'!K6
```

Dependențe: 'P0_Gates_v2'!K6

### B7

```excel
=IF(OR(NOT(ISNUMBER(B5)),NOT(ISNUMBER(B6)),NOT(ISNUMBER(B4))),"",IF(B4=0,"",(B5+B6)/B4))
```

Dependențe: B5, B6, B4, B4, B5, B6, B4

### E7

```excel
=IF(NOT(ISNUMBER(B7)),"",IF(B7<='Parametri'!B16,"CONCENTRAȚIE MICĂ","CONCENTRAȚIE DE ANALIZAT"))
```

Dependențe: B7, B7, 'Parametri'!B16

### B10

```excel
=IF(OR(NOT(ISNUMBER(B4)),NOT(ISNUMBER('Model_1X2'!K8))),"",ABS(B4-'Model_1X2'!K8))
```

Dependențe: B4, 'Model_1X2'!K8, B4, 'Model_1X2'!K8

### E10

```excel
=IF(NOT(ISNUMBER(B10)),"",IF(B10<='Parametri'!B10,"DIFERENȚĂ MICĂ","DIFERENȚĂ DE ANALIZAT"))
```

Dependențe: B10, B10, 'Parametri'!B10

### E11

```excel
=IF(B11="","NECOMPLETAT",IF(B11="NU","FĂRĂ SEMNAL","DE ANALIZAT"))
```

Dependențe: B11, B11

### B12

```excel
=IF(NOT(ISNUMBER('P0_Gates_v2'!I6)),"",'P0_Gates_v2'!I6)
```

Dependențe: 'P0_Gates_v2'!I6, 'P0_Gates_v2'!I6

### B13

```excel
=IF(NOT(ISNUMBER('P0_Gates_v2'!J6)),"",'P0_Gates_v2'!J6)
```

Dependențe: 'P0_Gates_v2'!J6, 'P0_Gates_v2'!J6

### B14

```excel
=IF(OR(NOT(ISNUMBER(B12)),NOT(ISNUMBER(B13))),"",MAX(B12,B13))
```

Dependențe: B12, B13, B12, B13

### E15

```excel
=P0_Gates_v2!K6
```

Dependențe: P0_Gates_v2!K6

### E16

```excel
=P0_Gates_v2!L6
```

Dependențe: P0_Gates_v2!L6

## Loss_Risk

### D4

```excel
='Parametri'!B20
```

Dependențe: 'Parametri'!B20

### E4

```excel
='Parametri'!B21
```

Dependențe: 'Parametri'!B21

### B5

```excel
=IF(NOT(ISNUMBER('Model_1X2'!D10)),"",'Model_1X2'!D10)
```

Dependențe: 'Model_1X2'!D10, 'Model_1X2'!D10

### C5

```excel
=IF(NOT(ISNUMBER('Model_1X2'!B10)),"",'Model_1X2'!B10)
```

Dependențe: 'Model_1X2'!B10, 'Model_1X2'!B10

### F5

```excel
='P0_Gates_v2'!L4
```

Dependențe: 'P0_Gates_v2'!L4

### G5

```excel
='P0_Gates_v2'!L5
```

Dependențe: 'P0_Gates_v2'!L5

### B6

```excel
=IF(NOT(ISNUMBER('Model_1X2'!L8)),"",'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!L8, 'Model_1X2'!L8

### C6

```excel
=IF(NOT(ISNUMBER('Model_1X2'!J8)),"",'Model_1X2'!J8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!J8

### B7

```excel
=IF(OR(NOT(ISNUMBER(B5)),NOT(ISNUMBER(B6))),"",ABS(B5-B6))
```

Dependențe: B5, B6, B5, B6

### C7

```excel
=IF(OR(NOT(ISNUMBER(C5)),NOT(ISNUMBER(C6))),"",ABS(C5-C6))
```

Dependențe: C5, C6, C5, C6

### F7

```excel
=IF(NOT(ISNUMBER(B7)),"",IF(B7<='Parametri'!B10,"DIFERENȚĂ MICĂ","DIFERENȚĂ DE ANALIZAT"))
```

Dependențe: B7, B7, 'Parametri'!B10

### G7

```excel
=IF(NOT(ISNUMBER(C7)),"",IF(C7<='Parametri'!B10,"DIFERENȚĂ MICĂ","DIFERENȚĂ DE ANALIZAT"))
```

Dependențe: C7, C7, 'Parametri'!B10

### F8

```excel
=IF(B8="","NECOMPLETAT",IF(B8="NU","FĂRĂ SEMNAL","DE ANALIZAT"))
```

Dependențe: B8, B8

### G8

```excel
=IF(C8="","NECOMPLETAT",IF(C8="NU","FĂRĂ SEMNAL","DE ANALIZAT"))
```

Dependențe: C8, C8

### F9

```excel
=IF(B9="","NECOMPLETAT",IF(B9="NU","FĂRĂ SEMNAL","DE ANALIZAT"))
```

Dependențe: B9, B9

### G9

```excel
=IF(C9="","NECOMPLETAT",IF(C9="NU","FĂRĂ SEMNAL","DE ANALIZAT"))
```

Dependențe: C9, C9

### B10

```excel
=P0_Gates_v2!C4
```

Dependențe: P0_Gates_v2!C4

### C10

```excel
=P0_Gates_v2!C5
```

Dependențe: P0_Gates_v2!C5

### B11

```excel
=P0_Gates_v2!H4
```

Dependențe: P0_Gates_v2!H4

### C11

```excel
=P0_Gates_v2!H5
```

Dependențe: P0_Gates_v2!H5

### B12

```excel
=P0_Gates_v2!L4
```

Dependențe: P0_Gates_v2!L4

### C12

```excel
=P0_Gates_v2!L5
```

Dependențe: P0_Gates_v2!L5

## Double_Chance

### B4

```excel
=IF(OR(NOT(ISNUMBER(Model_1X2!B10)),NOT(ISNUMBER(Model_1X2!C10))),"",Model_1X2!B10+Model_1X2!C10)
```

Dependențe: Model_1X2!B10, Model_1X2!C10, Model_1X2!B10, Model_1X2!C10

### D4

```excel
=IF(NOT(ISNUMBER(Model_1X2!D10)),"",Model_1X2!D10)
```

Dependențe: Model_1X2!D10, Model_1X2!D10

### E4

```excel
=IF(NOT(ISNUMBER('Uncertainty_v2'!B10)),"",'Uncertainty_v2'!B10)
```

Dependențe: 'Uncertainty_v2'!B10, 'Uncertainty_v2'!B10

### F4

```excel
=IF(OR(NOT(ISNUMBER(B4)),NOT(ISNUMBER(E4))),"",MAX(0,B4-E4))
```

Dependențe: B4, E4, B4, E4

### G4

```excel
=IF(NOT(ISNUMBER(Input_Meci!B31)),"",Input_Meci!B31)
```

Dependențe: Input_Meci!B31, Input_Meci!B31

### H4

```excel
=IF(OR(NOT(ISNUMBER('Model_1X2'!J8)),NOT(ISNUMBER('Model_1X2'!K8))),"",'Model_1X2'!J8+'Model_1X2'!K8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!K8, 'Model_1X2'!J8, 'Model_1X2'!K8

### I4

```excel
=IF(OR(NOT(ISNUMBER(F4)),NOT(ISNUMBER(H4))),"",F4-H4)
```

Dependențe: F4, H4, F4, H4

### J4

```excel
=""
```

Dependențe: 

### K4

```excel
=IF(AD4="CRITICAL MISSING","FAIL",IF(AD4<>"READY","INPUT",U4))
```

Dependențe: AD4, AD4, U4

### L4

```excel
=IF(OR(AD4<>"READY",NOT(ISNUMBER(B4)),NOT(ISNUMBER(Y4)),NOT(ISNUMBER(E4))),"",MIN('Parametri'!B43,ROUND(Y4*'Parametri'!B35+E4*'Parametri'!B36+IF(O4="PRUDENT",'Parametri'!B44,0)+IF(P4="PRUDENT",'Parametri'!B44,0)+IF(U4="FAIL",'Parametri'!B46,0),0)))
```

Dependențe: AD4, B4, Y4, E4, 'Parametri'!B43, Y4, 'Parametri'!B35, E4, 'Parametri'!B36, O4, 'Parametri'!B44, P4, 'Parametri'!B44, U4, 'Parametri'!B46

### M4

```excel
=IF(AD4="CRITICAL MISSING",5,IF(OR(AD4<>"READY",NOT(ISNUMBER(B4))),"",IF(OR(U4="FAIL",U4="WATCH"),5,IF(U4="INPUT","",MIN(5,IF(L4<='Parametri'!B39,1,IF(L4<='Parametri'!B40,2,IF(L4<='Parametri'!B41,3,IF(L4<='Parametri'!B42,4,5))))+AC4)))))
```

Dependențe: AD4, AD4, B4, U4, U4, U4, L4, 'Parametri'!B39, L4, 'Parametri'!B40, L4, 'Parametri'!B41, L4, 'Parametri'!B42, AC4

### N4

```excel
=IF(AD4="CRITICAL MISSING","NO BET",IF(AD4="INVALID","INPUT INVALID – NO RANK",IF(AD4<>"READY","VERIFICARE NECESARĂ – NO RANK",IF(U4="FAIL","NO BET",IF(U4="WATCH","WATCH",IF(OR(U4="INPUT",NOT(ISNUMBER(M4))),"NO RANK",IF(M4>=5,"WATCH",IF(AA4<>"YES","NO RANK",IF(M4=4,"RIDICAT",IF(M4=3,"MODERAT",IF(AND(M4=1,U4="PASS",F4>='Parametri'!B4),"DEFENSIV",IF(F4>='Parametri'!B5,"PRUDENT","MODERAT"))))))))))))
```

Dependențe: AD4, AD4, AD4, U4, U4, U4, M4, M4, AA4, M4, M4, M4, U4, F4, 'Parametri'!B4, F4, 'Parametri'!B5

### O4

```excel
=P0_Gates_v2!C4
```

Dependențe: P0_Gates_v2!C4

### P4

```excel
=P0_Gates_v2!H4
```

Dependențe: P0_Gates_v2!H4

### R4

```excel
=Uncertainty_v2!B5
```

Dependențe: Uncertainty_v2!B5

### S4

```excel
=Uncertainty_v2!B7
```

Dependențe: Uncertainty_v2!B7

### U4

```excel
=P0_Gates_v2!L4
```

Dependențe: P0_Gates_v2!L4

### V4

```excel
=IF(AD4<>"READY","Date: "&AD4,"Control="&U4&"; nivel="&TEXT(M4,"0")&"; Pfail="&TEXT(Y4,"0.0%")&"; haircut="&TEXT(E4,"0.0%")&"; fragilitate="&AB4)
```

Dependențe: AD4, AD4, U4, M4, Y4, E4, AB4

### W4

```excel
=IF(Input_Meci!B42="","",Input_Meci!B42)
```

Dependențe: Input_Meci!B42, Input_Meci!B42

### X4

```excel
=IF(NOT(ISNUMBER('Model_1X2'!L8)),"",'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!L8, 'Model_1X2'!L8

### Y4

```excel
=IF(OR(NOT(ISNUMBER(D4)),NOT(ISNUMBER(X4))),"",MAX(D4,X4))
```

Dependențe: D4, X4, D4, X4

### Z4

```excel
=P0_Gates_v2!C4
```

Dependențe: P0_Gates_v2!C4

### AA4

```excel
=IF(AND(AD4="READY",OR(U4="PASS",U4="PRUDENT"),ISNUMBER(M4),M4<5),"YES","NO")
```

Dependențe: AD4, U4, U4, M4, M4

### AB4

```excel
=Favorite_Fragility_v4!B12
```

Dependențe: Favorite_Fragility_v4!B12

### AC4

```excel
=Favorite_Fragility_v4!B13
```

Dependențe: Favorite_Fragility_v4!B13

### AD4

```excel
=IF('Model_1X2'!F14<>"READY",'Model_1X2'!F14,IF('Favorite_Fragility_v4'!B14="OPEN","PENDING","READY"))
```

Dependențe: 'Model_1X2'!F14, 'Model_1X2'!F14, 'Favorite_Fragility_v4'!B14

### AE4

```excel
=IF(AND(AA4="YES",N4="DEFENSIV"),"YES","NO")
```

Dependențe: AA4, N4

### AF4

```excel
=IF('WalkForward_Calibration'!B4=0,"FĂRĂ ISTORIC",IF('WalkForward_Calibration'!J4<>"PASS","N INSUFICIENT",'WalkForward_Calibration'!K4))
```

Dependențe: 'WalkForward_Calibration'!B4, 'WalkForward_Calibration'!J4, 'WalkForward_Calibration'!K4

### B5

```excel
=IF(OR(NOT(ISNUMBER(Model_1X2!C10)),NOT(ISNUMBER(Model_1X2!D10))),"",Model_1X2!C10+Model_1X2!D10)
```

Dependențe: Model_1X2!C10, Model_1X2!D10, Model_1X2!C10, Model_1X2!D10

### D5

```excel
=IF(NOT(ISNUMBER(Model_1X2!B10)),"",Model_1X2!B10)
```

Dependențe: Model_1X2!B10, Model_1X2!B10

### E5

```excel
=IF(NOT(ISNUMBER('Uncertainty_v2'!B10)),"",'Uncertainty_v2'!B10)
```

Dependențe: 'Uncertainty_v2'!B10, 'Uncertainty_v2'!B10

### F5

```excel
=IF(OR(NOT(ISNUMBER(B5)),NOT(ISNUMBER(E5))),"",MAX(0,B5-E5))
```

Dependențe: B5, E5, B5, E5

### G5

```excel
=IF(NOT(ISNUMBER(Input_Meci!B32)),"",Input_Meci!B32)
```

Dependențe: Input_Meci!B32, Input_Meci!B32

### H5

```excel
=IF(OR(NOT(ISNUMBER('Model_1X2'!K8)),NOT(ISNUMBER('Model_1X2'!L8))),"",'Model_1X2'!K8+'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!K8, 'Model_1X2'!L8, 'Model_1X2'!K8, 'Model_1X2'!L8

### I5

```excel
=IF(OR(NOT(ISNUMBER(F5)),NOT(ISNUMBER(H5))),"",F5-H5)
```

Dependențe: F5, H5, F5, H5

### J5

```excel
=""
```

Dependențe: 

### K5

```excel
=IF(AD5="CRITICAL MISSING","FAIL",IF(AD5<>"READY","INPUT",U5))
```

Dependențe: AD5, AD5, U5

### L5

```excel
=IF(OR(AD5<>"READY",NOT(ISNUMBER(B5)),NOT(ISNUMBER(Y5)),NOT(ISNUMBER(E5))),"",MIN('Parametri'!B43,ROUND(Y5*'Parametri'!B35+E5*'Parametri'!B36+IF(O5="PRUDENT",'Parametri'!B44,0)+IF(P5="PRUDENT",'Parametri'!B44,0)+T5+IF(U5="FAIL",'Parametri'!B46,0),0)))
```

Dependențe: AD5, B5, Y5, E5, 'Parametri'!B43, Y5, 'Parametri'!B35, E5, 'Parametri'!B36, O5, 'Parametri'!B44, P5, 'Parametri'!B44, T5, U5, 'Parametri'!B46

### M5

```excel
=IF(AD5="CRITICAL MISSING",5,IF(OR(AD5<>"READY",NOT(ISNUMBER(B5))),"",IF(OR(U5="FAIL",U5="WATCH"),5,IF(U5="INPUT","",MIN(5,IF(L5<='Parametri'!B39,1,IF(L5<='Parametri'!B40,2,IF(L5<='Parametri'!B41,3,IF(L5<='Parametri'!B42,4,5))))+AC5)))))
```

Dependențe: AD5, AD5, B5, U5, U5, U5, L5, 'Parametri'!B39, L5, 'Parametri'!B40, L5, 'Parametri'!B41, L5, 'Parametri'!B42, AC5

### N5

```excel
=IF(AD5="CRITICAL MISSING","NO BET",IF(AD5="INVALID","INPUT INVALID – NO RANK",IF(AD5<>"READY","VERIFICARE NECESARĂ – NO RANK",IF(U5="FAIL","NO BET",IF(U5="WATCH","WATCH",IF(OR(U5="INPUT",NOT(ISNUMBER(M5))),"NO RANK",IF(M5>=5,"WATCH",IF(AA5<>"YES","NO RANK",IF(M5=4,"RIDICAT",IF(M5=3,"MODERAT",IF(AND(M5=1,U5="PASS",F5>='Parametri'!B4),"DEFENSIV",IF(F5>='Parametri'!B5,"PRUDENT","MODERAT"))))))))))))
```

Dependențe: AD5, AD5, AD5, U5, U5, U5, M5, M5, AA5, M5, M5, M5, U5, F5, 'Parametri'!B4, F5, 'Parametri'!B5

### O5

```excel
=P0_Gates_v2!C5
```

Dependențe: P0_Gates_v2!C5

### P5

```excel
=P0_Gates_v2!H5
```

Dependențe: P0_Gates_v2!H5

### R5

```excel
=Uncertainty_v2!B5
```

Dependențe: Uncertainty_v2!B5

### S5

```excel
=Uncertainty_v2!B7
```

Dependențe: Uncertainty_v2!B7

### T5

```excel
=Uncertainty_v2!D13
```

Dependențe: Uncertainty_v2!D13

### U5

```excel
=P0_Gates_v2!L5
```

Dependențe: P0_Gates_v2!L5

### V5

```excel
=IF(AD5<>"READY","Date: "&AD5,"Control="&U5&"; nivel="&TEXT(M5,"0")&"; Pfail="&TEXT(Y5,"0.0%")&"; haircut="&TEXT(E5,"0.0%"))
```

Dependențe: AD5, AD5, U5, M5, Y5, E5

### W5

```excel
=IF(Input_Meci!B42="","",Input_Meci!B42)
```

Dependențe: Input_Meci!B42, Input_Meci!B42

### X5

```excel
=IF(NOT(ISNUMBER('Model_1X2'!J8)),"",'Model_1X2'!J8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!J8

### Y5

```excel
=IF(OR(NOT(ISNUMBER(D5)),NOT(ISNUMBER(X5))),"",MAX(D5,X5))
```

Dependențe: D5, X5, D5, X5

### Z5

```excel
=P0_Gates_v2!C5
```

Dependențe: P0_Gates_v2!C5

### AA5

```excel
=IF(AND(AD5="READY",OR(U5="PASS",U5="PRUDENT"),ISNUMBER(M5),M5<5),"YES","NO")
```

Dependențe: AD5, U5, U5, M5, M5

### AD5

```excel
=IF('Model_1X2'!F14<>"READY",'Model_1X2'!F14,IF(AND(ISNUMBER('Input_Meci'!C41),OR('Input_Meci'!C41=0,'Input_Meci'!C41=1,'Input_Meci'!C41=2)),"READY","PENDING"))
```

Dependențe: 'Model_1X2'!F14, 'Model_1X2'!F14, 'Input_Meci'!C41, 'Input_Meci'!C41, 'Input_Meci'!C41, 'Input_Meci'!C41

### AE5

```excel
=IF(AND(AA5="YES",N5="DEFENSIV"),"YES","NO")
```

Dependențe: AA5, N5

### AF5

```excel
=IF('WalkForward_Calibration'!B5=0,"FĂRĂ ISTORIC",IF('WalkForward_Calibration'!J5<>"PASS","N INSUFICIENT",'WalkForward_Calibration'!K5))
```

Dependențe: 'WalkForward_Calibration'!B5, 'WalkForward_Calibration'!J5, 'WalkForward_Calibration'!K5

### B6

```excel
=IF(OR(NOT(ISNUMBER(Model_1X2!B10)),NOT(ISNUMBER(Model_1X2!D10))),"",Model_1X2!B10+Model_1X2!D10)
```

Dependențe: Model_1X2!B10, Model_1X2!D10, Model_1X2!B10, Model_1X2!D10

### D6

```excel
=IF(NOT(ISNUMBER(Model_1X2!C10)),"",Model_1X2!C10)
```

Dependențe: Model_1X2!C10, Model_1X2!C10

### E6

```excel
=IF(NOT(ISNUMBER('Uncertainty_v2'!B10)),"",'Uncertainty_v2'!B10)
```

Dependențe: 'Uncertainty_v2'!B10, 'Uncertainty_v2'!B10

### F6

```excel
=IF(OR(NOT(ISNUMBER(B6)),NOT(ISNUMBER(E6))),"",MAX(0,B6-E6))
```

Dependențe: B6, E6, B6, E6

### G6

```excel
=IF(NOT(ISNUMBER(Input_Meci!B33)),"",Input_Meci!B33)
```

Dependențe: Input_Meci!B33, Input_Meci!B33

### H6

```excel
=IF(OR(NOT(ISNUMBER('Model_1X2'!J8)),NOT(ISNUMBER('Model_1X2'!L8))),"",'Model_1X2'!J8+'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!L8, 'Model_1X2'!J8, 'Model_1X2'!L8

### I6

```excel
=IF(OR(NOT(ISNUMBER(F6)),NOT(ISNUMBER(H6))),"",F6-H6)
```

Dependențe: F6, H6, F6, H6

### J6

```excel
=""
```

Dependențe: 

### K6

```excel
=IF(AD6="CRITICAL MISSING","FAIL",IF(AD6<>"READY","INPUT",U6))
```

Dependențe: AD6, AD6, U6

### L6

```excel
=IF(OR(AD6<>"READY",NOT(ISNUMBER(B6)),NOT(ISNUMBER(Y6)),NOT(ISNUMBER(E6))),"",MIN('Parametri'!B43,ROUND(Y6*'Parametri'!B37+E6*'Parametri'!B38+IF(Q6="PRUDENT",'Parametri'!B44,0)+IF(Q6="WATCH",'Parametri'!B45,0)+IF(Q6="FAIL",'Parametri'!B46,0),0)))
```

Dependențe: AD6, B6, Y6, E6, 'Parametri'!B43, Y6, 'Parametri'!B37, E6, 'Parametri'!B38, Q6, 'Parametri'!B44, Q6, 'Parametri'!B45, Q6, 'Parametri'!B46

### M6

```excel
=IF(AD6="CRITICAL MISSING",5,IF(OR(AD6<>"READY",NOT(ISNUMBER(B6))),"",IF(OR(U6="FAIL",U6="WATCH"),5,IF(U6="INPUT","",MIN(5,IF(L6<='Parametri'!B39,1,IF(L6<='Parametri'!B40,2,IF(L6<='Parametri'!B41,3,IF(L6<='Parametri'!B42,4,5))))+AC6)))))
```

Dependențe: AD6, AD6, B6, U6, U6, U6, L6, 'Parametri'!B39, L6, 'Parametri'!B40, L6, 'Parametri'!B41, L6, 'Parametri'!B42, AC6

### N6

```excel
=IF(AD6="CRITICAL MISSING","NO BET",IF(AD6="INVALID","INPUT INVALID – NO RANK",IF(AD6<>"READY","VERIFICARE NECESARĂ – NO RANK",IF(U6="FAIL","NO BET",IF(U6="WATCH","WATCH",IF(OR(U6="INPUT",NOT(ISNUMBER(M6))),"NO RANK",IF(M6>=5,"WATCH",IF(AA6<>"YES","NO RANK",IF(M6=4,"RIDICAT",IF(M6=3,"MODERAT",IF(OR(U6="PRUDENT",M6=2),"PRUDENT","DEFENSIV")))))))))))
```

Dependențe: AD6, AD6, AD6, U6, U6, U6, M6, M6, AA6, M6, M6, U6, M6

### Q6

```excel
=P0_Gates_v2!K6
```

Dependențe: P0_Gates_v2!K6

### R6

```excel
=Uncertainty_v2!B5
```

Dependențe: Uncertainty_v2!B5

### S6

```excel
=Uncertainty_v2!B7
```

Dependențe: Uncertainty_v2!B7

### U6

```excel
=P0_Gates_v2!L6
```

Dependențe: P0_Gates_v2!L6

### V6

```excel
=IF(AD6<>"READY","Date: "&AD6,"Control="&U6&"; nivel="&TEXT(M6,"0")&"; Pfail="&TEXT(Y6,"0.0%")&"; haircut="&TEXT(E6,"0.0%")&"; Pdraw ajustat="&TEXT(MAX('P0_Gates_v2'!I6,'P0_Gates_v2'!J6),"0.0%"))
```

Dependențe: AD6, AD6, U6, M6, Y6, E6, 'P0_Gates_v2'!I6, 'P0_Gates_v2'!J6

### W6

```excel
=IF(Input_Meci!B42="","",Input_Meci!B42)
```

Dependențe: Input_Meci!B42, Input_Meci!B42

### X6

```excel
=IF(NOT(ISNUMBER('Model_1X2'!K8)),"",'Model_1X2'!K8)
```

Dependențe: 'Model_1X2'!K8, 'Model_1X2'!K8

### Y6

```excel
=IF(OR(NOT(ISNUMBER(D6)),NOT(ISNUMBER(X6))),"",MAX(D6,X6))
```

Dependențe: D6, X6, D6, X6

### Z6

```excel
=P0_Gates_v2!K6
```

Dependențe: P0_Gates_v2!K6

### AA6

```excel
=IF(AND(AD6="READY",OR(U6="PASS",U6="PRUDENT"),ISNUMBER(M6),M6<5),"YES","NO")
```

Dependențe: AD6, U6, U6, M6, M6

### AD6

```excel
=IF('Model_1X2'!F14<>"READY",'Model_1X2'!F14,"READY")
```

Dependențe: 'Model_1X2'!F14, 'Model_1X2'!F14

### AE6

```excel
=IF(AND(AA6="YES",N6="DEFENSIV"),"YES","NO")
```

Dependențe: AA6, N6

### AF6

```excel
=IF('WalkForward_Calibration'!B6=0,"FĂRĂ ISTORIC",IF('WalkForward_Calibration'!J6<>"PASS","N INSUFICIENT",'WalkForward_Calibration'!K6))
```

Dependențe: 'WalkForward_Calibration'!B6, 'WalkForward_Calibration'!J6, 'WalkForward_Calibration'!K6

## Backtest

### J4

```excel
=IF(OR(NOT(ISNUMBER(G4)),NOT(ISNUMBER(I4))),"",G4-I4)
```

Dependențe: G4, I4, G4, I4

### K4

```excel
=IF(OR(NOT(ISNUMBER(G4)),NOT(ISNUMBER(H4)),H4<=1),"",G4*H4-1)
```

Dependențe: G4, H4, H4, G4, H4

### P4

```excel
=IF(OR(E4="",O4=""),"",IF(NOT(OR(O4="1",O4=1,O4="X",O4="2",O4=2)),"",IF(E4="1X",IF(OR(O4="1",O4=1,O4="X"),1,0),IF(E4="X2",IF(OR(O4="X",O4="2",O4=2),1,0),IF(OR(E4="12",E4=12),IF(OR(O4="1",O4=1,O4="2",O4=2),1,0),"")))))
```

Dependențe: E4, O4, O4, O4, O4, O4, O4, E4, O4, O4, O4, E4, O4, O4, O4, E4, E4, O4, O4, O4, O4

### Q4

```excel
=IF(OR(NOT(ISNUMBER(P4)),NOT(ISNUMBER(H4)),H4<=1),"",IF(P4=1,H4-1,-1))
```

Dependențe: P4, H4, H4, P4, H4

### W4

```excel
=IF(OR(NOT(ISNUMBER(G4)),G4<0,G4>1,NOT(ISNUMBER(P4))),"",(G4-P4)^2)
```

Dependențe: G4, G4, G4, P4, G4, P4

### X4

```excel
=IF(AND(ISNUMBER(A4),ISNUMBER(Y4),Y4<A4,AB4<>"",ISNUMBER(P4),ISNUMBER(G4),G4>=0,G4<=1,OR(M4="DEFENSIV",M4="PRUDENT",M4="MODERAT",M4="RIDICAT",M4="WATCH",M4="NO BET")),"YES","NO")
```

Dependențe: A4, Y4, Y4, A4, AB4, P4, G4, G4, G4, M4, M4, M4, M4, M4, M4

### Z4

```excel
=IF(AND(X4="YES",OR(M4="DEFENSIV",M4="PRUDENT",M4="MODERAT",M4="RIDICAT")),"YES","NO")
```

Dependențe: X4, M4, M4, M4, M4

### AA4

```excel
=IF(NOT(ISNUMBER(H4)),"MISSING",IF(AND(ISNUMBER(H4),H4>1),"VALID","INVALID"))
```

Dependențe: H4, H4, H4

### AC4

```excel
=IF(AND(NOT(ISNUMBER(A4)),E4="",NOT(ISNUMBER(G4)),M4="",O4=""),"INPUT",IF(X4="YES","VALID","INCOMPLETE / INVALID"))
```

Dependențe: A4, E4, G4, M4, O4, X4

### AD4

```excel
=IF(X4="YES",P4,"")
```

Dependențe: X4, P4

### AE4

```excel
=IF(X4="YES",W4,"")
```

Dependențe: X4, W4

### AF4

```excel
=IF(X4="YES",G4,"")
```

Dependențe: X4, G4

### AG4

```excel
=IF(AND(Z4="YES",AA4="VALID"),Q4,"")
```

Dependențe: Z4, AA4, Q4

### AH4

```excel
=IF(AND(Z4="YES",AA4="VALID"),"YES","NO")
```

Dependențe: Z4, AA4

## Dashboard

### B6

```excel
=IF(NOT(ISNUMBER('Double_Chance'!F4)),"",'Double_Chance'!F4)
```

Dependențe: 'Double_Chance'!F4, 'Double_Chance'!F4

### C6

```excel
=IF('Double_Chance'!K4="","",'Double_Chance'!K4)
```

Dependențe: 'Double_Chance'!K4, 'Double_Chance'!K4

### D6

```excel
=IF(NOT(ISNUMBER('Double_Chance'!L4)),"",'Double_Chance'!L4)
```

Dependențe: 'Double_Chance'!L4, 'Double_Chance'!L4

### E6

```excel
=IF(NOT(ISNUMBER('Double_Chance'!M4)),"",'Double_Chance'!M4)
```

Dependențe: 'Double_Chance'!M4, 'Double_Chance'!M4

### F6

```excel
=IF('Double_Chance'!AD4="","",'Double_Chance'!AD4)
```

Dependențe: 'Double_Chance'!AD4, 'Double_Chance'!AD4

### G6

```excel
=IF('Double_Chance'!N4="","",'Double_Chance'!N4)
```

Dependențe: 'Double_Chance'!N4, 'Double_Chance'!N4

### H6

```excel
=IF('Double_Chance'!AA4="","",'Double_Chance'!AA4)
```

Dependențe: 'Double_Chance'!AA4, 'Double_Chance'!AA4

### B7

```excel
=IF(NOT(ISNUMBER('Double_Chance'!F5)),"",'Double_Chance'!F5)
```

Dependențe: 'Double_Chance'!F5, 'Double_Chance'!F5

### C7

```excel
=IF('Double_Chance'!K5="","",'Double_Chance'!K5)
```

Dependențe: 'Double_Chance'!K5, 'Double_Chance'!K5

### D7

```excel
=IF(NOT(ISNUMBER('Double_Chance'!L5)),"",'Double_Chance'!L5)
```

Dependențe: 'Double_Chance'!L5, 'Double_Chance'!L5

### E7

```excel
=IF(NOT(ISNUMBER('Double_Chance'!M5)),"",'Double_Chance'!M5)
```

Dependențe: 'Double_Chance'!M5, 'Double_Chance'!M5

### F7

```excel
=IF('Double_Chance'!AD5="","",'Double_Chance'!AD5)
```

Dependențe: 'Double_Chance'!AD5, 'Double_Chance'!AD5

### G7

```excel
=IF('Double_Chance'!N5="","",'Double_Chance'!N5)
```

Dependențe: 'Double_Chance'!N5, 'Double_Chance'!N5

### H7

```excel
=IF('Double_Chance'!AA5="","",'Double_Chance'!AA5)
```

Dependențe: 'Double_Chance'!AA5, 'Double_Chance'!AA5

### B8

```excel
=IF(NOT(ISNUMBER('Double_Chance'!F6)),"",'Double_Chance'!F6)
```

Dependențe: 'Double_Chance'!F6, 'Double_Chance'!F6

### C8

```excel
=IF('Double_Chance'!K6="","",'Double_Chance'!K6)
```

Dependențe: 'Double_Chance'!K6, 'Double_Chance'!K6

### D8

```excel
=IF(NOT(ISNUMBER('Double_Chance'!L6)),"",'Double_Chance'!L6)
```

Dependențe: 'Double_Chance'!L6, 'Double_Chance'!L6

### E8

```excel
=IF(NOT(ISNUMBER('Double_Chance'!M6)),"",'Double_Chance'!M6)
```

Dependențe: 'Double_Chance'!M6, 'Double_Chance'!M6

### F8

```excel
=IF('Double_Chance'!AD6="","",'Double_Chance'!AD6)
```

Dependențe: 'Double_Chance'!AD6, 'Double_Chance'!AD6

### G8

```excel
=IF('Double_Chance'!N6="","",'Double_Chance'!N6)
```

Dependențe: 'Double_Chance'!N6, 'Double_Chance'!N6

### H8

```excel
=IF('Double_Chance'!AA6="","",'Double_Chance'!AA6)
```

Dependențe: 'Double_Chance'!AA6, 'Double_Chance'!AA6

### B21

```excel
='Double_Chance'!AF4
```

Dependențe: 'Double_Chance'!AF4

### B22

```excel
='Double_Chance'!AF5
```

Dependențe: 'Double_Chance'!AF5

### B23

```excel
='Double_Chance'!AF6
```

Dependențe: 'Double_Chance'!AF6

## P0_Gates_v2

### B4

```excel
=IF(NOT(ISNUMBER('Model_1X2'!L8)),"",'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!L8, 'Model_1X2'!L8

### C4

```excel
=IF(OR('Surse_Date'!L8<>"READY",NOT(ISNUMBER(B4))),"INPUT",IF(ROUND(B4,12)<='Parametri'!B20,"PASS",IF(ROUND(B4,12)<='Parametri'!B21,"PRUDENT","FAIL")))
```

Dependențe: 'Surse_Date'!L8, B4, B4, 'Parametri'!B20, B4, 'Parametri'!B21

### D4

```excel
=IF(NOT(ISNUMBER('Model_1X2'!J8)),"",'Model_1X2'!J8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!J8

### E4

```excel
=IF(OR(NOT(ISNUMBER(D4)),NOT(ISNUMBER(B4))),"",D4-B4)
```

Dependențe: D4, B4, D4, B4

### F4

```excel
=Input_Meci!B37
```

Dependențe: Input_Meci!B37

### G4

```excel
=IF(OR(NOT(ISNUMBER(B4)),NOT(ISNUMBER('Model_1X2'!D10))),"",B4-'Model_1X2'!D10)
```

Dependențe: B4, 'Model_1X2'!D10, B4, 'Model_1X2'!D10

### H4

```excel
=IF(OR(NOT(ISNUMBER(E4)),NOT(ISNUMBER(G4))),"INPUT",IF(ROUND(E4,12)>=0,"PASS",IF(ROUND(E4,12)>=-'Parametri'!B22,"PRUDENT",IF(AND('Input_Meci'!B37="DA",ROUND(G4,12)>='Parametri'!B23,'Input_Meci'!B39<>""),"PRUDENT","FAIL"))))
```

Dependențe: E4, G4, E4, E4, 'Parametri'!B22, 'Input_Meci'!B37, G4, 'Parametri'!B23, 'Input_Meci'!B39

### L4

```excel
=IF(OR(C4="INPUT",H4="INPUT"),"INPUT",IF(OR(C4="FAIL",H4="FAIL"),"FAIL",IF(OR(C4="PRUDENT",H4="PRUDENT"),"PRUDENT","PASS")))
```

Dependențe: C4, H4, C4, H4, C4, H4

### B5

```excel
=IF(NOT(ISNUMBER('Model_1X2'!J8)),"",'Model_1X2'!J8)
```

Dependențe: 'Model_1X2'!J8, 'Model_1X2'!J8

### C5

```excel
=IF(OR('Surse_Date'!L8<>"READY",NOT(ISNUMBER(B5))),"INPUT",IF(ROUND(B5,12)<='Parametri'!B20,"PASS",IF(ROUND(B5,12)<='Parametri'!B21,"PRUDENT","FAIL")))
```

Dependențe: 'Surse_Date'!L8, B5, B5, 'Parametri'!B20, B5, 'Parametri'!B21

### D5

```excel
=IF(NOT(ISNUMBER('Model_1X2'!L8)),"",'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!L8, 'Model_1X2'!L8

### E5

```excel
=IF(OR(NOT(ISNUMBER(D5)),NOT(ISNUMBER(B5))),"",D5-B5)
```

Dependențe: D5, B5, D5, B5

### F5

```excel
=Input_Meci!B38
```

Dependențe: Input_Meci!B38

### G5

```excel
=IF(OR(NOT(ISNUMBER(B5)),NOT(ISNUMBER('Model_1X2'!B10))),"",B5-'Model_1X2'!B10)
```

Dependențe: B5, 'Model_1X2'!B10, B5, 'Model_1X2'!B10

### H5

```excel
=IF(OR(NOT(ISNUMBER(E5)),NOT(ISNUMBER(G5))),"INPUT",IF(ROUND(E5,12)>=0,"PASS",IF(ROUND(E5,12)>=-'Parametri'!B22,"PRUDENT",IF(AND('Input_Meci'!B38="DA",ROUND(G5,12)>='Parametri'!B23,'Input_Meci'!B40<>""),"PRUDENT","FAIL"))))
```

Dependențe: E5, G5, E5, E5, 'Parametri'!B22, 'Input_Meci'!B38, G5, 'Parametri'!B23, 'Input_Meci'!B40

### L5

```excel
=IF(OR(C5="INPUT",H5="INPUT"),"INPUT",IF(OR(C5="FAIL",H5="FAIL"),"FAIL",IF(OR(C5="PRUDENT",H5="PRUDENT"),"PRUDENT","PASS")))
```

Dependențe: C5, H5, C5, H5, C5, H5

### I6

```excel
=IF(OR(NOT(ISNUMBER('Model_1X2'!C10)),NOT(ISNUMBER('Uncertainty_v2'!B10))),"",MIN(1,'Model_1X2'!C10+'Uncertainty_v2'!B10))
```

Dependențe: 'Model_1X2'!C10, 'Uncertainty_v2'!B10, 'Model_1X2'!C10, 'Uncertainty_v2'!B10

### J6

```excel
=IF(NOT(ISNUMBER('Model_1X2'!K8)),"",'Model_1X2'!K8)
```

Dependențe: 'Model_1X2'!K8, 'Model_1X2'!K8

### K6

```excel
=IF(OR('Surse_Date'!L8<>"READY",NOT(ISNUMBER(I6)),NOT(ISNUMBER(J6))),"INPUT",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B8,"PASS",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B9,"PRUDENT",IF(ROUND(MAX(I6,J6),12)<='Parametri'!B24,"WATCH","FAIL"))))
```

Dependențe: 'Surse_Date'!L8, I6, J6, I6, J6, 'Parametri'!B8, I6, J6, 'Parametri'!B9, I6, J6, 'Parametri'!B24

### L6

```excel
=K6
```

Dependențe: K6

## Uncertainty_v2

### B4

```excel
=IF(OR(COUNT('Input_Meci'!B36:C36)<>2,MIN('Input_Meci'!B36:C36)<0),"",MIN('Input_Meci'!B36:C36))
```

Dependențe: 'Input_Meci'!B36:C36, 'Input_Meci'!B36:C36, 'Input_Meci'!B36:C36

### D4

```excel
=IF(NOT(ISNUMBER(B4)),"INPUT",IF(B4<Parametri!B17,"SMALL SAMPLE","OK"))
```

Dependențe: B4, B4, Parametri!B17

### B5

```excel
=IF(NOT(ISNUMBER(B4)),"INPUT",IF(B4<Parametri!B17,"DA","NU"))
```

Dependențe: B4, B4, Parametri!B17

### D5

```excel
=B5
```

Dependențe: B5

### B6

```excel
=Input_Meci!B34
```

Dependențe: Input_Meci!B34

### D6

```excel
=B6
```

Dependențe: B6

### B7

```excel
=IF(OR(B5="INPUT",AND(B6<>"A",B6<>"B",B6<>"C")),"",IF(AND(B5="DA",B6="A"),"B",B6))
```

Dependențe: B5, B6, B6, B6, B5, B6, B6

### D7

```excel
=B7
```

Dependențe: B7

### B8

```excel
=IF(B7="A",Parametri!B13,IF(B7="B",Parametri!B14,IF(B7="C",Parametri!B15,"")))
```

Dependențe: B7, Parametri!B13, B7, Parametri!B14, B7, Parametri!B15

### D8

```excel
=B8
```

Dependențe: B8

### B9

```excel
=IF(B5="INPUT","",IF(B5="DA",'Parametri'!B25,0))
```

Dependențe: B5, B5, 'Parametri'!B25

### D9

```excel
=B9
```

Dependențe: B9

### B10

```excel
=IF(COUNT(B8:B9)<>2,"",B8+B9)
```

Dependențe: B8:B9, B8, B9

### D10

```excel
=B10
```

Dependențe: B10

### B13

```excel
=IF(NOT(ISNUMBER('Model_1X2'!L8)),"",'Model_1X2'!L8)
```

Dependențe: 'Model_1X2'!L8, 'Model_1X2'!L8

### C13

```excel
=IF(NOT(ISNUMBER('Input_Meci'!C41)),"",'Input_Meci'!C41)
```

Dependențe: 'Input_Meci'!C41, 'Input_Meci'!C41

### D13

```excel
=IF(OR(NOT(ISNUMBER(B13)),NOT(ISNUMBER(C13))),"",IF(B13<'Parametri'!B26,0,IF(C13=2,'Parametri'!B28,IF(C13=1,'Parametri'!B27,0))))
```

Dependențe: B13, C13, B13, 'Parametri'!B26, C13, 'Parametri'!B28, C13, 'Parametri'!B27

## WalkForward_Calibration

### B4

```excel
=COUNTIFS(Backtest!$E$4:$E$203,A4,Backtest!$X$4:$X$203,"YES")
```

Dependențe: Backtest!$E$4:$E$203, A4, Backtest!$X$4:$X$203

### C4

```excel
=SUMIFS('Backtest'!$AD$4:$AD$203,'Backtest'!$E$4:$E$203,A4,'Backtest'!$X$4:$X$203,"YES")
```

Dependențe: 'Backtest'!$AD$4:$AD$203, 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$X$4:$X$203

### D4

```excel
=IF(B4=0,"",C4/B4)
```

Dependențe: B4, C4, B4

### E4

```excel
=IF(B4=0,"",SUMIFS('Backtest'!$AF$4:$AF$203,'Backtest'!$E$4:$E$203,A4,'Backtest'!$X$4:$X$203,"YES")/B4)
```

Dependențe: B4, 'Backtest'!$AF$4:$AF$203, 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$X$4:$X$203, B4

### F4

```excel
=IF(OR(NOT(ISNUMBER(D4)),NOT(ISNUMBER(E4))),"",D4-E4)
```

Dependențe: D4, E4, D4, E4

### G4

```excel
=IF(B4=0,"",SUMIFS('Backtest'!$AE$4:$AE$203,'Backtest'!$E$4:$E$203,A4,'Backtest'!$X$4:$X$203,"YES")/B4)
```

Dependențe: B4, 'Backtest'!$AE$4:$AE$203, 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$X$4:$X$203, B4

### H4

```excel
=IF(M4=0,"",SUMIFS('Backtest'!$AG$4:$AG$203,'Backtest'!$E$4:$E$203,A4,'Backtest'!$AH$4:$AH$203,"YES"))
```

Dependențe: M4, 'Backtest'!$AG$4:$AG$203, 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$AH$4:$AH$203

### I4

```excel
=IF(M4=0,"",H4/M4)
```

Dependențe: M4, H4, M4

### J4

```excel
=IF(B4>=Parametri!B29,"PASS","INSUFFICIENT N")
```

Dependențe: B4, Parametri!B29

### K4

```excel
=IF(NOT(ISNUMBER(F4)),"INPUT",IF(ABS(F4)<=Parametri!B30,"PASS","RECALIBRATE"))
```

Dependențe: F4, F4, Parametri!B30

### L4

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A4,'Backtest'!$Z$4:$Z$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$Z$4:$Z$203

### M4

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A4,'Backtest'!$AH$4:$AH$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$AH$4:$AH$203

### N4

```excel
=IF(L4=0,"",SUMIFS('Backtest'!$P$4:$P$203,'Backtest'!$E$4:$E$203,A4,'Backtest'!$Z$4:$Z$203,"YES")/L4)
```

Dependențe: L4, 'Backtest'!$P$4:$P$203, 'Backtest'!$E$4:$E$203, A4, 'Backtest'!$Z$4:$Z$203, L4

### B5

```excel
=COUNTIFS(Backtest!$E$4:$E$203,A5,Backtest!$X$4:$X$203,"YES")
```

Dependențe: Backtest!$E$4:$E$203, A5, Backtest!$X$4:$X$203

### C5

```excel
=SUMIFS('Backtest'!$AD$4:$AD$203,'Backtest'!$E$4:$E$203,A5,'Backtest'!$X$4:$X$203,"YES")
```

Dependențe: 'Backtest'!$AD$4:$AD$203, 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$X$4:$X$203

### D5

```excel
=IF(B5=0,"",C5/B5)
```

Dependențe: B5, C5, B5

### E5

```excel
=IF(B5=0,"",SUMIFS('Backtest'!$AF$4:$AF$203,'Backtest'!$E$4:$E$203,A5,'Backtest'!$X$4:$X$203,"YES")/B5)
```

Dependențe: B5, 'Backtest'!$AF$4:$AF$203, 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$X$4:$X$203, B5

### F5

```excel
=IF(OR(NOT(ISNUMBER(D5)),NOT(ISNUMBER(E5))),"",D5-E5)
```

Dependențe: D5, E5, D5, E5

### G5

```excel
=IF(B5=0,"",SUMIFS('Backtest'!$AE$4:$AE$203,'Backtest'!$E$4:$E$203,A5,'Backtest'!$X$4:$X$203,"YES")/B5)
```

Dependențe: B5, 'Backtest'!$AE$4:$AE$203, 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$X$4:$X$203, B5

### H5

```excel
=IF(M5=0,"",SUMIFS('Backtest'!$AG$4:$AG$203,'Backtest'!$E$4:$E$203,A5,'Backtest'!$AH$4:$AH$203,"YES"))
```

Dependențe: M5, 'Backtest'!$AG$4:$AG$203, 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$AH$4:$AH$203

### I5

```excel
=IF(M5=0,"",H5/M5)
```

Dependențe: M5, H5, M5

### J5

```excel
=IF(B5>=Parametri!B29,"PASS","INSUFFICIENT N")
```

Dependențe: B5, Parametri!B29

### K5

```excel
=IF(NOT(ISNUMBER(F5)),"INPUT",IF(ABS(F5)<=Parametri!B30,"PASS","RECALIBRATE"))
```

Dependențe: F5, F5, Parametri!B30

### L5

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A5,'Backtest'!$Z$4:$Z$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$Z$4:$Z$203

### M5

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A5,'Backtest'!$AH$4:$AH$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$AH$4:$AH$203

### N5

```excel
=IF(L5=0,"",SUMIFS('Backtest'!$P$4:$P$203,'Backtest'!$E$4:$E$203,A5,'Backtest'!$Z$4:$Z$203,"YES")/L5)
```

Dependențe: L5, 'Backtest'!$P$4:$P$203, 'Backtest'!$E$4:$E$203, A5, 'Backtest'!$Z$4:$Z$203, L5

### B6

```excel
=COUNTIFS(Backtest!$E$4:$E$203,A6,Backtest!$X$4:$X$203,"YES")
```

Dependențe: Backtest!$E$4:$E$203, A6, Backtest!$X$4:$X$203

### C6

```excel
=SUMIFS('Backtest'!$AD$4:$AD$203,'Backtest'!$E$4:$E$203,A6,'Backtest'!$X$4:$X$203,"YES")
```

Dependențe: 'Backtest'!$AD$4:$AD$203, 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$X$4:$X$203

### D6

```excel
=IF(B6=0,"",C6/B6)
```

Dependențe: B6, C6, B6

### E6

```excel
=IF(B6=0,"",SUMIFS('Backtest'!$AF$4:$AF$203,'Backtest'!$E$4:$E$203,A6,'Backtest'!$X$4:$X$203,"YES")/B6)
```

Dependențe: B6, 'Backtest'!$AF$4:$AF$203, 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$X$4:$X$203, B6

### F6

```excel
=IF(OR(NOT(ISNUMBER(D6)),NOT(ISNUMBER(E6))),"",D6-E6)
```

Dependențe: D6, E6, D6, E6

### G6

```excel
=IF(B6=0,"",SUMIFS('Backtest'!$AE$4:$AE$203,'Backtest'!$E$4:$E$203,A6,'Backtest'!$X$4:$X$203,"YES")/B6)
```

Dependențe: B6, 'Backtest'!$AE$4:$AE$203, 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$X$4:$X$203, B6

### H6

```excel
=IF(M6=0,"",SUMIFS('Backtest'!$AG$4:$AG$203,'Backtest'!$E$4:$E$203,A6,'Backtest'!$AH$4:$AH$203,"YES"))
```

Dependențe: M6, 'Backtest'!$AG$4:$AG$203, 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$AH$4:$AH$203

### I6

```excel
=IF(M6=0,"",H6/M6)
```

Dependențe: M6, H6, M6

### J6

```excel
=IF(B6>=Parametri!B29,"PASS","INSUFFICIENT N")
```

Dependențe: B6, Parametri!B29

### K6

```excel
=IF(NOT(ISNUMBER(F6)),"INPUT",IF(ABS(F6)<=Parametri!B30,"PASS","RECALIBRATE"))
```

Dependențe: F6, F6, Parametri!B30

### L6

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A6,'Backtest'!$Z$4:$Z$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$Z$4:$Z$203

### M6

```excel
=COUNTIFS('Backtest'!$E$4:$E$203,A6,'Backtest'!$AH$4:$AH$203,"YES")
```

Dependențe: 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$AH$4:$AH$203

### N6

```excel
=IF(L6=0,"",SUMIFS('Backtest'!$P$4:$P$203,'Backtest'!$E$4:$E$203,A6,'Backtest'!$Z$4:$Z$203,"YES")/L6)
```

Dependențe: L6, 'Backtest'!$P$4:$P$203, 'Backtest'!$E$4:$E$203, A6, 'Backtest'!$Z$4:$Z$203, L6

## Favorite_Fragility_v4

### B5

```excel
=Input_Meci!B43
```

Dependențe: Input_Meci!B43

### B6

```excel
=IF(Uncertainty_v2!B5="DA","DA",IF(Uncertainty_v2!B5="NU","NU","PENDING"))
```

Dependențe: Uncertainty_v2!B5, Uncertainty_v2!B5

### B7

```excel
=Input_Meci!B44
```

Dependențe: Input_Meci!B44

### B8

```excel
=Input_Meci!B45
```

Dependențe: Input_Meci!B45

### B9

```excel
=Input_Meci!B46
```

Dependențe: Input_Meci!B46

### B11

```excel
=COUNTIF(B6:B9,"DA")
```

Dependențe: B6:B9

### B12

```excel
=IF(B5="NU","N/A",IF(B5<>"DA","PENDING",IF(COUNTIF(B6:B9,"DA")+COUNTIF(B6:B9,"NU")<>4,"PENDING",IF(B11>='Parametri'!B48,"MATERIAL",IF(B11=1,"REVIEW","PASS")))))
```

Dependențe: B5, B5, B6:B9, B6:B9, B11, 'Parametri'!B48, B11

### B13

```excel
=IF(B12="MATERIAL",'Parametri'!B49,0)
```

Dependențe: B12, 'Parametri'!B49

### B14

```excel
=IF(B5="NU","N/A",IF(AND(B12<>"PENDING",'Surse_Date'!L12="READY"),"CLOSED","OPEN"))
```

Dependențe: B5, B12, 'Surse_Date'!L12

## Surse_Date

### L5

```excel
=IF(OR(C5="NOT AVAILABLE",C5="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C5="VERIFIED",C5="DERIVED",C5="PRIOR / SHRINKAGE"),IF(OR(D5="",COUNT(E5:F5)<>2,I5="",J5="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J5<>"DA",E5>'Input_Meci'!B6,F5>'Input_Meci'!B6,F5>E5),"INVALID","READY")),"PENDING"))
```

Dependențe: C5, C5, C5, C5, C5, D5, E5:F5, I5, J5, 'Input_Meci'!B6, J5, E5, 'Input_Meci'!B6, F5, 'Input_Meci'!B6, F5, E5

### L6

```excel
=IF(OR(C6="NOT AVAILABLE",C6="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C6="VERIFIED",C6="DERIVED",C6="PRIOR / SHRINKAGE"),IF(OR(D6="",COUNT(E6:F6)<>2,I6="",J6="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J6<>"DA",E6>'Input_Meci'!B6,F6>'Input_Meci'!B6,F6>E6),"INVALID","READY")),"PENDING"))
```

Dependențe: C6, C6, C6, C6, C6, D6, E6:F6, I6, J6, 'Input_Meci'!B6, J6, E6, 'Input_Meci'!B6, F6, 'Input_Meci'!B6, F6, E6

### L7

```excel
=IF(OR(C7="NOT AVAILABLE",C7="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C7="VERIFIED",C7="DERIVED",C7="PRIOR / SHRINKAGE"),IF(OR(D7="",COUNT(E7:F7)<>2,I7="",J7="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J7<>"DA",E7>'Input_Meci'!B6,F7>'Input_Meci'!B6,F7>E7),"INVALID","READY")),"PENDING"))
```

Dependențe: C7, C7, C7, C7, C7, D7, E7:F7, I7, J7, 'Input_Meci'!B6, J7, E7, 'Input_Meci'!B6, F7, 'Input_Meci'!B6, F7, E7

### D8

```excel
=IF('Input_Meci'!B42="","",'Input_Meci'!B42)
```

Dependențe: 'Input_Meci'!B42, 'Input_Meci'!B42

### L8

```excel
=IF(OR(C8="NOT AVAILABLE",C8="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C8="VERIFIED",C8="DERIVED",C8="PRIOR / SHRINKAGE"),IF(OR(D8="",COUNT(E8:F8)<>2,I8="",J8="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J8<>"DA",E8>'Input_Meci'!B6,F8>'Input_Meci'!B6,F8>E8),"INVALID","READY")),"PENDING"))
```

Dependențe: C8, C8, C8, C8, C8, D8, E8:F8, I8, J8, 'Input_Meci'!B6, J8, E8, 'Input_Meci'!B6, F8, 'Input_Meci'!B6, F8, E8

### G9

```excel
=IF(NOT(ISNUMBER('Input_Meci'!B36)),"",'Input_Meci'!B36)
```

Dependențe: 'Input_Meci'!B36, 'Input_Meci'!B36

### H9

```excel
=IF(NOT(ISNUMBER('Input_Meci'!C36)),"",'Input_Meci'!C36)
```

Dependențe: 'Input_Meci'!C36, 'Input_Meci'!C36

### L9

```excel
=IF(OR(C9="NOT AVAILABLE",C9="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(COUNT(G9:H9)<>2,NOT(ISNUMBER('Input_Meci'!B36)),NOT(ISNUMBER('Input_Meci'!C36))),"PENDING",IF(OR(MIN(G9:H9)<0,MOD(G9,1)<>0,MOD(H9,1)<>0),"INVALID",IF(OR(C9="NOT AVAILABLE",C9="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C9="VERIFIED",C9="DERIVED",C9="PRIOR / SHRINKAGE",C9="SMALL SAMPLE"),IF(OR(D9="",COUNT(E9:F9)<>2,I9="",J9="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J9<>"DA",E9>'Input_Meci'!B6,F9>'Input_Meci'!B6,F9>E9),"INVALID","READY")),"PENDING")))))
```

Dependențe: C9, C9, G9:H9, 'Input_Meci'!B36, 'Input_Meci'!C36, G9:H9, G9, H9, C9, C9, C9, C9, C9, C9, D9, E9:F9, I9, J9, 'Input_Meci'!B6, J9, E9, 'Input_Meci'!B6, F9, 'Input_Meci'!B6, F9, E9

### L10

```excel
=IF(L9<>"READY","PENDING",IF(MIN(G9:H9)>='Parametri'!B17,"N/A",IF(OR(C10="NOT AVAILABLE",C10="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(COUNT(G10:H10)<>2,K10<>"INTEGRAT IN MODELE"),"PENDING",IF(MIN(G10:H10)<=0,"INVALID",IF(OR(C10="NOT AVAILABLE",C10="SOURCE CONFLICT"),"CRITICAL MISSING",IF(OR(C10="VERIFIED",C10="DERIVED",C10="PRIOR / SHRINKAGE"),IF(OR(D10="",COUNT(E10:F10)<>2,I10="",J10="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J10<>"DA",E10>'Input_Meci'!B6,F10>'Input_Meci'!B6,F10>E10),"INVALID","READY")),"PENDING")))))))
```

Dependențe: L9, G9:H9, 'Parametri'!B17, C10, C10, G10:H10, K10, G10:H10, C10, C10, C10, C10, C10, D10, E10:F10, I10, J10, 'Input_Meci'!B6, J10, E10, 'Input_Meci'!B6, F10, 'Input_Meci'!B6, F10, E10

### L11

```excel
=IF(OR(K11="IMPACT NEREZOLVAT",C11="SOURCE CONFLICT"),"REVIEW",IF(OR(AND(C11="PENDING OFFICIAL",K11="REFRESH PRE-XI"),AND(OR(C11="NOT AVAILABLE",C11="PROXY ONLY"),OR(K11="INTEGRAT IN MODELE",K11="FARA IMPACT MATERIAL"))),IF(IF(OR(D11="",COUNT(E11:F11)<>2,I11="",J11="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J11<>"DA",E11>'Input_Meci'!B6,F11>'Input_Meci'!B6,F11>E11),"INVALID","READY"))="READY","CONDITIONAL",IF(OR(D11="",COUNT(E11:F11)<>2,I11="",J11="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J11<>"DA",E11>'Input_Meci'!B6,F11>'Input_Meci'!B6,F11>E11),"INVALID","READY"))),IF(OR(K11="INTEGRAT IN MODELE",K11="FARA IMPACT MATERIAL"),IF(OR(C11="NOT AVAILABLE",C11="SOURCE CONFLICT"),"REVIEW",IF(OR(C11="VERIFIED",C11="DERIVED",C11="PRIOR / SHRINKAGE"),IF(OR(D11="",COUNT(E11:F11)<>2,I11="",J11="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J11<>"DA",E11>'Input_Meci'!B6,F11>'Input_Meci'!B6,F11>E11),"INVALID","READY")),"PENDING")),"PENDING")))
```

Dependențe: K11, C11, C11, K11, C11, C11, K11, K11, D11, E11:F11, I11, J11, 'Input_Meci'!B6, J11, E11, 'Input_Meci'!B6, F11, 'Input_Meci'!B6, F11, E11, D11, E11:F11, I11, J11, 'Input_Meci'!B6, J11, E11, 'Input_Meci'!B6, F11, 'Input_Meci'!B6, F11, E11, K11, K11, C11, C11, C11, C11, C11, D11, E11:F11, I11, J11, 'Input_Meci'!B6, J11, E11, 'Input_Meci'!B6, F11, 'Input_Meci'!B6, F11, E11

### L12

```excel
=IF('Input_Meci'!B43="NU","N/A",IF('Input_Meci'!B43<>"DA","PENDING",IF(OR(C12="NOT AVAILABLE",C12="SOURCE CONFLICT"),"REVIEW",IF(OR(C12="VERIFIED",C12="DERIVED",C12="PRIOR / SHRINKAGE"),IF(OR(D12="",COUNT(E12:F12)<>2,I12="",J12="",NOT(ISNUMBER('Input_Meci'!B6))),"PENDING",IF(OR(J12<>"DA",E12>'Input_Meci'!B6,F12>'Input_Meci'!B6,F12>E12),"INVALID","READY")),"PENDING"))))
```

Dependențe: 'Input_Meci'!B43, 'Input_Meci'!B43, C12, C12, C12, C12, C12, D12, E12:F12, I12, J12, 'Input_Meci'!B6, J12, E12, 'Input_Meci'!B6, F12, 'Input_Meci'!B6, F12, E12

### L15

```excel
=IF(COUNTIF(L5:L10,"CRITICAL MISSING")>0,"CRITICAL MISSING",IF(COUNTIF(L5:L11,"INVALID")>0,"INVALID",IF(OR(COUNTIF(L5:L11,"PENDING")>0,COUNTIF(L5:L11,"REVIEW")>0),"PENDING",IF(L11="CONDITIONAL","CONDITIONAL","READY"))))
```

Dependențe: L5:L10, L5:L11, L5:L11, L5:L11, L11
