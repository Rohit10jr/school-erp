givenstring = 'Venzo Technologies'
substring = 'no'
i=0
j=0
count=0
while(i<len(givenstring)):
    while(j<len(substring)):
        if (givenstring[i] == substring[j]):
            print("given: ", givenstring[i], "substr: ", substring[j])

            i+=1
            j+=1
            if 1 == j:
                count+=1
                print("count",count)     
        else:
            i+=1

if count == 1:
    print("substring is present")
else:
    print("substring not is present")


