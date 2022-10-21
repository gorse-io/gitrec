# gitrec

油猴脚本

![image](https://user-images.githubusercontent.com/38517192/197133356-0c201648-3e75-45f1-b3eb-f6ff0fdd556c.png)

## 使用

- 安装依赖 `pnpm i`
- 开发调试 `pnpm serve`
- 打包构建 `pnpm build`

### 注意事项

github.com 启用了 [CSP](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CSP), 必须关闭 CSP 才能让开发调试正常工作

![img](https://user-images.githubusercontent.com/38517192/167983257-97dd69d3-70a6-444e-870b-9ec89858911e.png)

相关文档 [vite-plugin-monkey/README_zh.md#csp](https://github.com/lisonge/vite-plugin-monkey/blob/main/README_zh.md#csp)

### 工具文档

- vite [cn.vitejs.dev/guide](https://cn.vitejs.dev/guide/)
- vite-plugin-monkey [README_zh.md](https://github.com/lisonge/vite-plugin-monkey/blob/main/README_zh.md)

## 可优化

- 可以使用 react/vue 组件 代替 手动拼接html字符串, 并且获得 模块热替换 功能
- src/colors.ts 代码重复度过高
- GM_xmlhttpRequest 太过底层, 需要二次包装模拟 fetch
