// This will get imported in main.js
export const logSomething = msg => {
    setTimeout(console.log.bind(console, "%c\n" + msg, "font-family:'Helvetica Neue', Helvetica, Arial, PingFangTC-Light, 'Microsoft YaHei', 微软雅黑, 'STHeiti Light', STXihei, '华文细黑', Heiti, 黑体, sans-serif; font-size: 20px"));
};

export const logSomethingBig = msg => {
    setTimeout(console.log.bind(console, "%c\n" + msg, "color: red; font-weight: bold; font-family:'Helvetica Neue', Helvetica, Arial, PingFangTC-Light, 'Microsoft YaHei', 微软雅黑, 'STHeiti Light', STXihei, '华文细黑', Heiti, 黑体, sans-serif; font-size: 48px; text-shadow: -1px 1px 0 #000, 1px 1px 0 #000,1px -1px 0 #000, -1px -1px 0 #000;"));
};
