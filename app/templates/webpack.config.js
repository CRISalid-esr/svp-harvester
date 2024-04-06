const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
    entry: './src/js/main.js',
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, '../static/js')
    },
    resolve: {
        fallback: {"crypto": false, "path": false, "os": false, "fs": false}
    },
    module: {
        rules: [
            {
                test: /\.(scss)$/,
                use: [
                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            postcssOptions: {
                                plugins: () => [
                                    require('autoprefixer')
                                ]
                            }
                        }
                    },
                    {
                        loader: 'sass-loader'
                    }
                ]
            },
            // from https://stackoverflow.com/a/74992564
            {
                rules: [{
                    test: /\.woff2?$/,
                    type: "asset/resource",
                }]
            }
        ]
    },
    plugins: [
        new CopyWebpackPlugin({
            patterns: [
                {from: 'images', to: path.resolve(__dirname, '../static/images')}
            ]
        })
    ]
}
