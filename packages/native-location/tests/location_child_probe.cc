#include <cstdio>
#include <cstring>

// Isolated test target only. No path/DB/credentials/network/model operations.
// The sole lifetime is stdin until EOF; no stdout/stderr payload is emitted.
int main(int argc, char** argv) {
  if (argc != 2 || std::strcmp(argv[1], "--hold-until-eof") != 0) return 64;
  while (std::getchar() != EOF) {}
  return std::ferror(stdin) ? 1 : 0;
}
