---
applyTo: "**/*.java"
description: Java/Spring Boot コーディング規約
---

# Java/Spring Boot Instructions

## コーディング規約

- Google Java Style Guideに準拠
- Lombokの適切な使用
- Stream APIの活用
- Spring Bootのベストプラクティス

## Lombok

```java
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.Builder;

@Data
@Builder
@RequiredArgsConstructor
public class User {
    private final String id;
    private final String name;
    private final String email;
}
```

## Spring Boot コントローラー

```java
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping("/{id}")
    public ResponseEntity<User> getUser(@PathVariable String id) {
        return userService.findById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User createUser(@Valid @RequestBody UserCreateRequest request) {
        return userService.create(request);
    }
}
```

## サービス層

```java
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;

    public Optional<User> findById(String id) {
        return userRepository.findById(id);
    }

    @Transactional
    public User create(UserCreateRequest request) {
        var user = User.builder()
            .name(request.getName())
            .email(request.getEmail())
            .build();
        return userRepository.save(user);
    }
}
```

## リポジトリ

```java
@Repository
public interface UserRepository extends JpaRepository<User, String> {

    Optional<User> findByEmail(String email);

    List<User> findByNameContaining(String name);
}
```

## Stream API

```java
// Stream API を活用
List<String> names = users.stream()
    .filter(u -> u.isActive())
    .map(User::getName)
    .sorted()
    .collect(Collectors.toList());

// Optional の適切な使用
userRepository.findById(id)
    .map(this::toDto)
    .orElseThrow(() -> new NotFoundException("User not found"));
```

## エラーハンドリング

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleNotFound(NotFoundException ex) {
        return new ErrorResponse(ex.getMessage());
    }

    @ExceptionHandler(ValidationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidation(ValidationException ex) {
        return new ErrorResponse(ex.getMessage());
    }
}
```

## テスト

- JUnit 5 / TestNG を使用
- Mockito でモック作成
- @SpringBootTest で統合テスト

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void findById_shouldReturnUser_whenExists() {
        // Arrange
        var user = User.builder().id("1").name("Test").build();
        when(userRepository.findById("1")).thenReturn(Optional.of(user));

        // Act
        var result = userService.findById("1");

        // Assert
        assertThat(result).isPresent();
        assertThat(result.get().getName()).isEqualTo("Test");
    }
}
```

## コマンド

```bash
cd java-backend
mvn compile           # コンパイル
mvn spring-boot:run   # 開発サーバー
mvn test              # テスト
mvn package           # パッケージング
```
