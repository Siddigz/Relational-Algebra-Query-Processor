
def parse_text(text):
    pass


def main():

    try:
        with open("input.txt", "r") as inputFile:
            text = inputFile.read()

    except FileNotFoundError:
        print("ERROR - input.txt not found")    
        quit()
    
    parse_text(text)


    with open("output.txt", "w") as outputFile:
        outputFile.write("test123")
        pass
    
    print("SUCCESSFUL - output.txt has been filled with results")
    


if __name__ == "__main__":
    main()
