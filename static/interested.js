function Interested() {
    
    const [added, setAdded] = React.useState('');
    const handleSubmit=(event)=>{
        event.preventDefault();
        const newName=event.target.elements.name.value;
        const newEmail=event.target.elements.email.value;
        const newPhone=event.target.elements.phone.value;
        axios.post("/add_interested", {name:newName, email:newEmail, phone:newPhone}).then(
            response=>setAdded(response.data[0])
        ) 
    }
    return (
        <div class='in_interested' >
            <div >
                <div class="ad1">interested?</div>  
                <div class="ad1">Intrigued?</div> 
                <div class="ad2">Leave details and we will get back to you:</div> 
            </div>
            <div>
                <form onSubmit={handleSubmit}>
                    <input type="text" name="name" placeholder="Your name" autoFocus required/>
                    <input type="email" name="email" placeholder="Email" title="example@example.com" required/>
                    <input type="tel" name="phone" placeholder="Phone" title="example: 050-1234567"  pattern="[0-9]{3}-[0-9]{7}" required/>
                    <input type="submit" value="Send"/>
                </form>
            </div>
            <div class="added_info">
                {added}
            </div>
        </div>
    )
}


ReactDOM.render(<Interested />, document.getElementById("interested"));