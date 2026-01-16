n,t = map(int,input().strip().split())

s=input().strip()
s=list(s)
while t>0:
    b=0
    while b<len(s)-1:

        if s[b]=='B' and s[b+1]=='G':
            s[b],s[b+1]=s[b+1],s[b]
            b+=2
        else:
            b+=1

    t-=1

print("".join(s))