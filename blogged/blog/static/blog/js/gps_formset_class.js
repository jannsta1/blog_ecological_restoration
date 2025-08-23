

class GpsFormset {

    constructor() {

        var totalFroms = 1;
        const emptyFormId = ;

    }

    addForm() {
        const formIndex = parseInt(this.totalForms);
        let emptyFormHtml = document.getElementById(emptyFormId).innerHTML.replace(/__prefix__/g, formIndex);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = emptyFormHtml.trim();
        const formEl = tempDiv.firstChild;

        formList.appendChild(formEl);

        this.totalForms = this.totalForms + 1;
    }

    removeForm() {
        const formDiv = event.target.closest('.image-form, .gps-form');
        const deleteField = formDiv.querySelector(`input[type="checkbox"][name$="-DELETE"]`);
        
        formDiv.remove();
        this.totalForms = this.totalForms - 1;
        
    }



}