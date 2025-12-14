# 泛型和抽象类封装service

用泛型和抽象类封装service

## 抽象类

父类定义一个方法，每一个子类的实现内容是不一样的，没法抽取到父类变成通用方法。父类不能调用子类的方法，此时需要将父类改为抽象类abstract，在父类中定义抽象方法体，要求在子类继承时必须实现，这样在运行时代码就会自动调用对应子类实现的方法。

以下是一个使用泛型和抽象类封装基础 Service 层 CRUD 操作的 Java 代码示例：

```java
import java.util.List;

// 定义泛型抽象类BaseService，封装基础CRUD操作
abstract class BaseService<T, V, M extends BaseMapperPlus<T, V>> {

    protected M mapper;

    public BaseService(M mapper) {
        this.mapper = mapper;
    }

    // 分页列表查询
    public PageResult<V> findPage(int pageNum, int pageSize) {
        // 调用Mapper的分页查询方法
        List<V> list = mapper.selectVoPage(pageNum, pageSize);
        // 计算总记录数
        int totalCount = mapper.count();
        return new PageResult<>(pageNum, pageSize, totalCount, list);
    }

    // 详情查询
    public V findById(int id) {
        return mapper.selectVoById(id);
    }

    // 新增操作
    public void save(T entity) {
        // 保存前参数校验，由子类实现
        validEntityBeforeSave(entity);
        mapper.insert(entity);
    }

    // 修改操作
    public void update(T entity) {
        // 修改前参数校验，由子类实现
        validEntityBeforeUpdate(entity);
        mapper.update(entity);
    }

    // 批量删除操作
    public void deleteByIds(List<Integer> ids) {
        mapper.deleteByIds(ids);
    }

    // 抽象方法，子类必须实现保存前参数校验逻辑
    protected abstract void validEntityBeforeSave(T entity);

    // 抽象方法，子类必须实现修改前参数校验逻辑
    protected abstract void validEntityBeforeUpdate(T entity);
}

// 定义BaseMapperPlus接口，作为Mapper的基础接口
interface BaseMapperPlus<T, V> {

    List<V> selectVoPage(int pageNum, int pageSize);

    V selectVoById(int id);

    void insert(T entity);

    void update(T entity);

    void deleteByIds(List<Integer> ids);

    int count();
}

// 具体业务Service实现类，继承BaseService
class UserService extends BaseService<User, UserVO, UserMapper> {

    public UserService(UserMapper mapper) {
        super(mapper);
    }

    @Override
    protected void validEntityBeforeSave(User entity) {
        // 实现用户保存前参数校验逻辑
        if (entity.getUsername() == null || entity.getPassword() == null) {
            throw new IllegalArgumentException("用户名和密码不能为空");
        }
    }

    @Override
    protected void validEntityBeforeUpdate(User entity) {
        // 实现用户修改前参数校验逻辑
        if (entity.getId() == null) {
            throw new IllegalArgumentException("用户ID不能为空");
        }
    }
}

// 定义用户实体类
class User {

    private Integer id;
    private String username;
    private String password;

    // 省略getter和setter方法
}

// 定义用户VO类，用于展示数据
class UserVO {

    private Integer id;
    private String username;

    // 省略getter和setter方法
}

// 定义用户Mapper接口，继承BaseMapperPlus
interface UserMapper extends BaseMapperPlus<User, UserVO> {

    // 具体业务查询方法
    List<UserVO> selectVoPage(int pageNum, int pageSize);

    UserVO selectVoById(int id);

    void insert(User entity);

    void update(User entity);

    void deleteByIds(List<Integer> ids);

    int count();
}

// 分页结果类
class PageResult<T> {

    private int pageNum;
    private int pageSize;
    private int totalCount;
    private List<T> data;

    public PageResult(int pageNum, int pageSize, int totalCount, List<T> data) {
        this.pageNum = pageNum;
        this.pageSize = pageSize;
        this.totalCount = totalCount;
        this.data = data;
    }

    // 省略getter方法
}
```

使用示例：

```java
public class Main {

    public static void main(String[] args) {
        // 初始化Mapper和Service
        UserMapper userMapper = new UserMapperImpl();
        UserService userService = new UserService(userMapper);

        // 分页查询用户列表
        PageResult<UserVO> pageResult = userService.findPage(1, 10);
        System.out.println("总记录数：" + pageResult.getTotalCount());
        System.out.println("当前页数据：" + pageResult.getData());

        // 新增用户
        User user = new User();
        user.setUsername("testuser");
        user.setPassword("testpassword");
        userService.save(user);

        // 修改用户
        user.setUsername("updateduser");
        userService.update(user);

        // 删除用户
        userService.deleteByIds(List.of(user.getId()));
    }
}
```

这个示例展示了如何通过泛型和抽象类封装基础 Service 层 CRUD 操作，具体特点包括：

- 使用泛型`<T, V, M>`分别代表实体类、视图类和 Mapper 接口，实现代码的通用性。
- 抽象类`BaseService`封装了基础 CRUD 方法，通过抽象方法`validEntityBeforeSave`和`validEntityBeforeUpdate`强制子类实现参数校验逻辑。
- 具体业务 Service 类（如`UserService`）继承`BaseService`，并实现抽象方法，完成个性化业务逻辑。
- Mapper 接口继承`BaseMapperPlus`，定义具体的数据库操作方法。

通过这种方式，开发者可以快速实现基础 CRUD 功能，减少重复代码，提升开发效率。