function User(){
    const [user, setUser] = React.useState('');
    const getUser = () => {
        axios.get('/user_detail').then((result) => {
            console.log(result.data)
            setUser(result.data.name);
        })
    }
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (
            <div>
                <h4>Hello {user}- what do you want to do?</h4> 
            </div>
        );
}
ReactDOM.render(<User/>, document.getElementById('hello'))