module.exports = {
    plugins: {
        'autoprefixer': {},
        'postcss-import': {},
        'postcss-nested': {},
        'cssnano': process.env.NODE_ENV === 'production' ? {} : false
    }
};
