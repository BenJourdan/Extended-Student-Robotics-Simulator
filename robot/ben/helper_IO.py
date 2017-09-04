

def write_list_to_file(file,list):

    with open(file,"w") as file:
        for row in list:
            file.write(" ".join([str(a) for a in row])+"\n")


def load_list_from_file(file):
    ls=[]
    st=[]
    with open(file,"r") as file:
        st=file.readlines()

    for line in st:
        ls.append(map(float,line.strip("\n").split(" ")))
    return ls






