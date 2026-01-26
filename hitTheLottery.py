amt = int(input().strip())
denoms=[1,5,10,20,100]
ans=0

for i in range(len(denoms)-1,-1,-1):
    curr = amt//denoms[i]
    amt-= denoms[i] * curr
    ans+=curr
    
print(ans)