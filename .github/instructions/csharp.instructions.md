---
applyTo: "**/*.cs"
description: C#/.NET コーディング規約
---

# C#/.NET Instructions

## コーディング規約

- .NET コーディング規約に準拠
- Nullable参照型を有効化
- async/awaitパターンを使用
- DIコンテナを活用

## Nullable参照型

```csharp
#nullable enable

public class UserService
{
    public User? GetUser(string id)
    {
        // null許容型を明示
    }

    public User GetUserOrThrow(string id)
    {
        return GetUser(id) ?? throw new NotFoundException();
    }
}
```

## 非同期処理

```csharp
public async Task<User> GetUserAsync(string id, CancellationToken ct = default)
{
    return await _repository.FindAsync(id, ct);
}

// Task を返すメソッドは Async サフィックス
public async Task<IEnumerable<User>> ListUsersAsync()
{
    return await _repository.GetAllAsync();
}
```

## 依存性注入

```csharp
// Program.cs
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IUserRepository, UserRepository>();

// コンストラクタインジェクション
public class UserService : IUserService
{
    private readonly IUserRepository _repository;

    public UserService(IUserRepository repository)
    {
        _repository = repository;
    }
}
```

## Web API コントローラー

```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;

    public UsersController(IUserService userService)
    {
        _userService = userService;
    }

    [HttpGet("{id}")]
    [ProducesResponseType(typeof(User), 200)]
    [ProducesResponseType(404)]
    public async Task<ActionResult<User>> GetUser(string id)
    {
        var user = await _userService.GetUserAsync(id);
        return user is null ? NotFound() : Ok(user);
    }
}
```

## エラーハンドリング

```csharp
public class GlobalExceptionHandler : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext context,
        Exception exception,
        CancellationToken ct)
    {
        // 例外を適切に処理
    }
}
```

## テスト

- xUnit / NUnit / MSTest を使用
- AAA パターン (Arrange-Act-Assert)
- Moq でモック作成

```csharp
public class UserServiceTests
{
    [Fact]
    public async Task GetUser_ReturnsUser_WhenExists()
    {
        // Arrange
        var mockRepo = new Mock<IUserRepository>();
        mockRepo.Setup(r => r.FindAsync("1", default))
                .ReturnsAsync(new User { Id = "1" });

        var service = new UserService(mockRepo.Object);

        // Act
        var result = await service.GetUserAsync("1");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("1", result.Id);
    }
}
```

## コマンド

```bash
dotnet build
dotnet run --project csharp-backend/
dotnet test csharp-backend.Tests/
dotnet test batch-csharp.Tests/
```
