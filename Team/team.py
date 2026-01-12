n = int(input().strip())
arr=[[int(x) for x in input().strip().split()] for _ in range(n)]
ans=0
for i in range(n):
    curr=0
    for j in range(n):
        if arr[i][j]==1:
            curr+=1
    if curr>=2:
        ans+=1

print(ans)