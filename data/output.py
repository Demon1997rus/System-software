def main():
    counter = 0
    limit = 5
    test = 0
    test1 = 5
    while True:
        counter += 1;
        while True:
            test += 1;
            while True:
                test1 -= 1;
                if not (test1 > 0):
                    break
            if not (test < 5):
                break
        if not (counter < limit):
            break

if __name__ == "__main__":
    main()
