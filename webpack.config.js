const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'bundle.js',
    publicPath: '/'
  },
  devtool: 'source-map',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.js', '.jsx']
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html'
    })
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
      publicPath: '/'
    },
    port: 3000,
    hot: true,
    historyApiFallback: {
      rewrites: [
        { from: /^\/(?!.*\.(js|css|png|jpg|jpeg|gif|ico|json)$).*$/, to: '/index.html' }
      ]
    },
    compress: true,
    setupMiddlewares: (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      // Add custom middleware to handle errors properly
      middlewares.unshift({
        name: 'error-handler',
        middleware: (err, req, res, next) => {
          if (!res.headersSent) {
            res.status(500).json({ error: err.message });
          } else {
            console.error('Error after response was sent:', err);
          }
        }
      });

      // Add middleware to prevent multiple responses
      middlewares.unshift({
        name: 'prevent-multiple-responses',
        middleware: (req, res, next) => {
          if (res.headersSent) {
            return next();
          }
          next();
        }
      });

      return middlewares;
    }
  }
}; 