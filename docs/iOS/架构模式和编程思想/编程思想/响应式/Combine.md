# Combine

`Combine`是Apple在iOS 13及以上版本中引入的一个框架，用于处理响应式编程和数据绑定。它与`RxSwift`类似，但它是Apple官方的解决方案。`Combine`提供了许多与`RxSwift`相似的功能，但在某些方面更紧密地集成到Apple的生态系统中。

**`viewA`、`viewB`、`viewC`是三个独立的UIView，通过一个共享的ViewModel来实现数据同步更新。以下是一个完整的示例。**

1. **创建ViewModel**：
   创建一个`SharedViewModel`类，并使用`@Published`属性来自动通知视图更新。

```swift
import UIKit
import Combine

class SharedViewModel {
    @Published var sharedData: String = ""
    
    // 你可以添加更多的共享数据和方法
}
```

2. **创建视图**：
   创建三个视图（ViewA、ViewB、ViewC），并将它们绑定到同一个ViewModel实例。

```swift
import UIKit
import Combine

class ViewA: UIView {
    private var viewModel: SharedViewModel!
    private var cancellables: Set<AnyCancellable> = []
    
    private let textField: UITextField = {
        let textField = UITextField()
        textField.borderStyle = .roundedRect
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    init(viewModel: SharedViewModel) {
        self.viewModel = viewModel
        super.init(frame: .zero)
        setupView()
        bindViewModel()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupView() {
        addSubview(textField)
        
        NSLayoutConstraint.activate([
            textField.centerXAnchor.constraint(equalTo: centerXAnchor),
            textField.centerYAnchor.constraint(equalTo: centerYAnchor),
            textField.widthAnchor.constraint(equalToConstant: 200)
        ])
        
        textField.addTarget(self, action: #selector(textFieldDidChange(_:)), for: .editingChanged)
    }
    
    private func bindViewModel() {
        viewModel.$sharedData
            .sink { [weak self] newValue in
                self?.textField.text = newValue
            }
            .store(in: &cancellables)
    }
    
    @objc private func textFieldDidChange(_ textField: UITextField) {
        viewModel.sharedData = textField.text ?? ""
    }
}

class ViewB: UIView {
    private var viewModel: SharedViewModel!
    private var cancellables: Set<AnyCancellable> = []
    
    private let label: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    init(viewModel: SharedViewModel) {
        self.viewModel = viewModel
        super.init(frame: .zero)
        setupView()
        bindViewModel()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupView() {
        addSubview(label)
        
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: centerXAnchor),
            label.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }
    
    private func bindViewModel() {
        viewModel.$sharedData
            .sink { [weak self] newValue in
                self?.label.text = newValue
            }
            .store(in: &cancellables)
    }
}

class ViewC: UIView {
    private var viewModel: SharedViewModel!
    private var cancellables: Set<AnyCancellable> = []
    
    private let label: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    init(viewModel: SharedViewModel) {
        self.viewModel = viewModel
        super.init(frame: .zero)
        setupView()
        bindViewModel()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupView() {
        addSubview(label)
        
        NSLayoutConstraint.activate([
            label.centerXAnchor.constraint(equalTo: centerXAnchor),
            label.centerYAnchor.constraint(equalTo: centerYAnchor)
        ])
    }
    
    private func bindViewModel() {
        viewModel.$sharedData
            .sink { [weak self] newValue in
                self?.label.text = newValue
            }
            .store(in: &cancellables)
    }
}
```

3. **在父视图控制器中使用ViewModel**：
   在一个父视图控制器中创建ViewModel实例，并将它传递给子视图。

```swift
import UIKit

class ParentViewController: UIViewController {
    private let viewModel = SharedViewModel()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let viewA = ViewA(viewModel: viewModel)
        let viewB = ViewB(viewModel: viewModel)
        let viewC = ViewC(viewModel: viewModel)
        
        viewA.translatesAutoresizingMaskIntoConstraints = false
        viewB.translatesAutoresizingMaskIntoConstraints = false
        viewC.translatesAutoresizingMaskIntoConstraints = false
        
        view.addSubview(viewA)
        view.addSubview(viewB)
        view.addSubview(viewC)
        
        NSLayoutConstraint.activate([
            viewA.topAnchor.constraint(equalTo: view.topAnchor),
            viewA.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            viewA.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            viewA.heightAnchor.constraint(equalTo: view.heightAnchor, multiplier: 1/3),
            
            viewB.topAnchor.constraint(equalTo: viewA.bottomAnchor),
            viewB.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            viewB.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            viewB.heightAnchor.constraint(equalTo: view.heightAnchor, multiplier: 1/3),
            
            viewC.topAnchor.constraint(equalTo: viewB.bottomAnchor),
            viewC.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            viewC.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            viewC.heightAnchor.constraint(equalTo: view.heightAnchor, multiplier: 1/3)
        ])
    }
}
```

通过这种方式，`viewA`、`viewB`、`viewC`都共享同一个ViewModel实例。当ViewModel中的数据发生变化时，所有绑定到它的视图都会自动更新，从而实现同步更新。