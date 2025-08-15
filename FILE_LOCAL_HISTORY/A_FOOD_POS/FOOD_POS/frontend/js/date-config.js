// ไฟล์กำหนดค่ารูปแบบวันที่และเวลาแบบรวมศูนย์
// แก้ไขที่นี่ที่เดียวเพื่อเปลี่ยนรูปแบบวันที่ทั้งระบบ

// การตั้งค่ารูปแบบวันที่และเวลา
const DATE_CONFIG = {
    // ตั้งค่าโซนเวลา
    timeZone: 'Asia/Bangkok',
    
    // ตั้งค่ารูปแบบวันที่และเวลาแบบเต็ม
    fullDateTime: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    },
    
    // ตั้งค่ารูปแบบเฉพาะวันที่
    dateOnly: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    },
    
    // ตั้งค่ารูปแบบเฉพาะเวลา
    timeOnly: {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    },
    
    // เครื่องหมายคั่นวันที่ (เปลี่ยนจาก - เป็น /)
    dateSeparator: '/',
    
    // ภาษาที่ใช้ (ใช้ th-TH เพื่อแสดงเวลาไทยที่ถูกต้อง)
    locale: 'th-TH'
};

// ฟังก์ชันจัดรูปแบบวันที่และเวลาแบบเต็ม
function formatDateTime(dateString) {
    if (!dateString) return '';
    
    let date;
    
    // ตรวจสอบรูปแบบเวลาจาก SQLite (YYYY-MM-DD HH:MM:SS)
    if (typeof dateString === 'string' && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(dateString)) {
        // เพิ่ม timezone offset สำหรับเวลาไทย (+07:00)
        date = new Date(dateString + '+07:00');
    } else {
        date = new Date(dateString);
    }
    
    if (isNaN(date.getTime())) return dateString; // ถ้าแปลงไม่ได้ให้คืนค่าเดิม
    
    return date.toLocaleString(DATE_CONFIG.locale, {
        timeZone: DATE_CONFIG.timeZone,
        ...DATE_CONFIG.fullDateTime
    }).replace(/-/g, DATE_CONFIG.dateSeparator);
}

// ฟังก์ชันจัดรูปแบบเฉพาะวันที่
function formatDateOnly(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleString(DATE_CONFIG.locale, {
        timeZone: DATE_CONFIG.timeZone,
        ...DATE_CONFIG.dateOnly
    }).replace(/-/g, DATE_CONFIG.dateSeparator);
}

// ฟังก์ชันจัดรูปแบบเฉพาะเวลา
function formatTimeOnly(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleString(DATE_CONFIG.locale, {
        timeZone: DATE_CONFIG.timeZone,
        ...DATE_CONFIG.timeOnly
    });
}

// ฟังก์ชันสำหรับวันที่และเวลาปัจจุบัน
function getCurrentDateTime() {
    return formatDateTime(new Date());
}

function getCurrentDateOnly() {
    return formatDateOnly(new Date());
}

function getCurrentTimeOnly() {
    return formatTimeOnly(new Date());
}

// Export สำหรับใช้งานในไฟล์อื่น
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DATE_CONFIG,
        formatDateTime,
        formatDateOnly,
        formatTimeOnly,
        getCurrentDateTime,
        getCurrentDateOnly,
        getCurrentTimeOnly
    };
}