CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?=
LDLIBS ?= -lm

.PHONY: all test clean
all: test

rcme-test: src/rcme.c src/rcme_domain.c tests/test_rcme.c include/rcme.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -Iinclude src/rcme.c src/rcme_domain.c tests/test_rcme.c $(LDLIBS) -o $@

test: rcme-test
	./rcme-test

clean:
	rm -f rcme-test
