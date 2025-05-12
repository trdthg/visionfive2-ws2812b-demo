const ESLintPlugin = require('eslint-webpack-plugin');

const options = {
    extensions: [`js`],
    exclude: [
        `node_modules`,
    ],
}

module.exports = {
    plugins: [new ESLintPlugin(options)],
    entry: './src/js/main.js',
    output: {
        path: __dirname + '/dist',
        filename: 'bundle.js'
    },
    module: {
        rules: [{
                test: /\.(scss)$/,
                use: [{
                    loader: 'style-loader', // inject CSS to page
                }, {
                    loader: 'css-loader', // translates CSS into CommonJS modules
                }, {
                    loader: 'postcss-loader', // Run post css actions
                    options: {
                        plugins: function () { // post css plugins, can be exported to postcss.config.js
                            return [
                                require('precss'),
                                require('autoprefixer')
                            ];
                        }
                    }
                }, {
                    loader: 'sass-loader', // compiles Sass to CSS
                    options: {
                        includePaths: ["node_modules"]
                    }
                }]
            },
            {
                test: /.m?js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
            // },
            // {
            //     test: /\.(ttf|eot|woff(2)?)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
            //     use: [{
            //         loader: 'file-loader',
            //         options: {
            //             name: '[name].[ext]',
            //             outputPath: 'fonts/'
            //         }
            //     }]
            // }
        ]
    }
}